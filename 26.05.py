from music21.serial import ToneRow
from music21 import corpus, converter, metadata, analysis, meter, key, stream, instrument, note
import sys


class Grader:
    def __init__(self, link):
        self.link = link

    def run(self):
        test = converter.parse(self.link)
        ms = test.measures(numberStart=1, numberEnd=len(test.measureOffsetMap()))
        staves = list(ms.recurse().getElementsByClass(stream.PartStaff))
        left = staves[-1]
        right = staves[0]

        l_notation = self.__form_list(left)
        r_notation = self.__form_list(right)

        info_list_notes1, info_list_time1 = self.__make_list_notes(r_notation, -1)
        info_list_notes2, info_list_time2 = self.__make_list_notes(l_notation, -1)

        for n in range(0, len(info_list_notes1) - 1, 2):
            self.__modify(info_list_notes1, info_list_notes2, info_list_time1, info_list_time2, n)

        for measure in range(0, len(info_list_notes2) - 1, 2):
            i = 0
            while i < len(info_list_notes1[measure]) - 1:
                if info_list_notes1[measure][i] == info_list_notes1[measure][i + 1]:
                    if info_list_notes1[measure + 1][i] == info_list_notes1[measure + 1][i + 1]:
                        if info_list_notes2[measure][i] == info_list_notes2[measure][i + 1]:
                            if info_list_notes2[measure + 1][i] == info_list_notes2[measure + 1][i + 1]:
                                #                       print('spotted repetitions in %s' % measure)
                                info_list_notes1[measure].pop(i)
                                info_list_notes1[measure + 1].pop(i)
                                info_list_notes2[measure].pop(i)
                                info_list_notes2[measure + 1].pop(i)
                            else:
                                i += 1
                        else:
                            i += 1
                    else:
                        i += 1
                else:
                    i += 1

        voice1 = ''
        voice2 = ''
        voice3 = ''
        voice4 = ''
        chord_number = []

        for n in range(0, len(info_list_notes1) - 1, 2):
            chord_number.append(len(info_list_notes1[n]))
            voice1 += self.__stringify(info_list_notes1[n])
            voice2 += self.__stringify(info_list_notes1[n + 1])
            voice3 += self.__stringify(info_list_notes2[n])
            voice4 += self.__stringify(info_list_notes2[n + 1])

        self.intervalize(voice1, voice2, chord_number, 'soprano/alto')
        self.intervalize(voice1, voice3, chord_number, 'soprano/tenor')
        self.intervalize(voice1, voice4, chord_number, 'soprano/bass')
        self.intervalize(voice2, voice3, chord_number, 'alto/tenor')
        self.intervalize(voice2, voice4, chord_number, 'alto/bass')
        self.intervalize(voice3, voice4, chord_number, 'tenor/bass')

    @staticmethod
    def __extract_data(statement, index):
        return statement.strip("<>").split(" ")[index]

    def __form_list(self, obj):
        notation = []
        vcs = list(obj.recurse().getElementsByClass(stream.Voice))
        for vc in vcs:
            l = list(vc.notes)
            notation.append((l, self.__extract_data(str(vc), -1)))
        return notation

    def __make_list_notes(self, list_notation, index):
        info_list = []
        info_list_time = []
        for stuff in list_notation:
            measure_l = []
            measure_l_t = []
            for note in stuff[0]:
                measure_l.append(self.__extract_data(str(note), index))
                measure_l_t.append(float(self.__extract_data(str(note.duration), index)))
            info_list.append(measure_l)
            info_list_time.append(measure_l_t)
        return info_list, info_list_time

    @staticmethod
    def __modify(notation1, notation2, time1, time2, msr_index):

        v1min = min(time1[msr_index])
        v2min = min(time1[msr_index + 1])
        v3min = min(time2[msr_index])
        v4min = min(time2[msr_index + 1])
        total_min = min(v1min, v2min, v3min, v4min)

        def edit(div_min, list_n, list_notes):
            n = 0
            for _ in range(len(list_n)):
                factor = int(list_n[n] / div_min)
                if factor > 1:
                    for _ in range(factor - 1):
                        list_n.insert(n + 1, list_n[n])
                        list_notes.insert(n + 1, list_notes[n])
                    n += factor
                elif factor == 1:
                    n += 1

        edit(total_min, time1[msr_index], notation1[msr_index])
        edit(total_min, time1[msr_index + 1], notation1[msr_index + 1])
        edit(total_min, time2[msr_index], notation2[msr_index])
        edit(total_min, time2[msr_index + 1], notation2[msr_index + 1])

    @staticmethod
    def __stringify(measure_list):
        str_fragment = "%s/4" % len(measure_list) + "\t"
        for note in measure_list:
            str_fragment += note + "\t"
        return str_fragment

    @staticmethod
    def intervalize(voice_a, voice_b, chords, voice_abr):
        def check(intervals, chord_list, vc_abr, step, info=''):
            for i in range(len(intervals) - step):
                if intervals[i] == intervals[i + step]:
                    if interval_list[i] in "P5 P1 P-4 P-1":
                        n = 0
                        sum_beat = chord_list[n]
                        while i >= sum_beat:
                            n += 1
                            sum_beat += chord_list[n]
                        print('%s' % info + 'parallel or repetitive %s' % intervals[i] + ' in measure %s ' % (n + 1),
                              vc_abr)
                    else:
                        pass

        interval_list = []
        stream1 = converter.parse('tinynotation: %s' % voice_a, makeNotation=False)
        stream2 = converter.parse('tinynotation: %s' % voice_b, makeNotation=False)
        stream2.attachIntervalsBetweenStreams(stream1)
        for n in stream2.notes:
            if n.editorial.harmonicInterval is None:
                pass
            else:
                interval_list.append(n.editorial.harmonicInterval.directedName)
        #   print(interval_list)
        check(interval_list, chords, voice_abr, 1)
        check(interval_list, chords, voice_abr, 2, 'hidden ')


if __name__ == "__main__":
    path = Grader(sys.argv[1])
    path.run()
