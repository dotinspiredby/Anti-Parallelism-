from music21.serial import ToneRow, pcToToneRow
from music21 import corpus, converter, metadata, analysis, meter, key, stream, instrument, note, pitch

test = converter.parse('C:/Users/garfi/python_advanced/harmony_grader/test2.xml')

test_score = test.voicesToParts()


def partify(score):
    for i in range(1, 3):
        for j in range(2):
            yield score.parts["P1-Staff{0}-v{1}".format(i, j)]


def intervalize(voice_1, voice_2, voice_names):
    def make_interval_list(voice_a, voice_b, direction, vc_abr):
        interval_list = []
        for measure_index in range(len(voice_a.elements)):
            measure_intervals = []
            voice_a.elements[measure_index].flat.attachIntervalsBetweenStreams(voice_b.elements[measure_index].flat)
            for n in voice_a.elements[measure_index].notes:

                if n.editorial.harmonicInterval is None:
                    pass
                else:
                    if direction == "down" and "-" not in n.editorial.harmonicInterval.directedName:
                        if n.editorial.harmonicInterval.directedName != "P1":
                            print("voice crossing {0} in measure {1}".format(voice_names,
                                                                             voice_a.elements[
                                                                                 measure_index].notes.index(n)))
                    elif direction == "up" and "-" in n.editorial.harmonicInterval.directedName:
                        print("voice crossing {0} in measure {1}".format(voice_names,
                                                                         voice_a.elements[measure_index].notes.index(
                                                                             n)))

                    if "-" in n.editorial.harmonicInterval.directedName:
                        measure_intervals.append(n.editorial.harmonicInterval.directedName.replace("-", ""))
                    else:
                        measure_intervals.append(n.editorial.harmonicInterval.directedName)
                    # measure_intervals.append(n.editorial.harmonicInterval.directedName)

            interval_list.append(measure_intervals)
        return interval_list

    def fill(list_a, list_b):
        n = 0
        len1 = len(list_a)
        len2 = len(list_b)
        while n < len1:
            try:
                if list_a[n] == list_b[n]:
                    n += 1
                else:
                    try:
                        i_for_a = list_b.index(list_a[n])
                        for i in range(i_for_a - 1, n - 1, -1):
                            list_a.insert(n, list_b[i])
                            len1 += 1
                    except ValueError:
                        i_for_b = list_a.index(list_b[n])
                        for i in range(i_for_b - 1, n - 1, -1):
                            list_b.insert(n, list_a[i])
                            len2 += 1
                    n += 1
            except IndexError:
                return max(list_a, list_b)

        return list_b

    def check(intervals, vc_abr, step, index_map, info=''):
        for i in range(len(intervals) - int(step)):
            fifths = ['P5', 'P12', 'P19']
            octaves = ['P1', 'P8', 'P15']
            if intervals[i] == intervals[i + step]:

                type_of_error = ""
                if intervals[i] in fifths and intervals[i + step] in fifths:  # interval_list in the past
                    type_of_error = "fifths"
                elif intervals[i] in octaves and intervals[i + step] in octaves:
                    type_of_error = "octaves"
                else:
                    pass
                if type_of_error:
                    measure_num = 0
                    for interval_num in index_map:
                        if i < interval_num:
                            measure_num = index_map.index(interval_num) + 1
                            break

                    print('%s' % info + 'parallel or repetitive %s' % type_of_error + ' in measure %s ' % measure_num,
                          vc_abr)

    intrvls_up_down = make_interval_list(voice_1, voice_2, "up",
                                         voice_names)  # здесь проверить на перечение - наличие минуса в интервале
    intrvls_down_up = make_interval_list(voice_2, voice_1, "down", voice_names)

    interval_list = []
    beats = []
    beat_num = 0
    for cell in range(len(intrvls_up_down)):  # вписать контекст
        measure = fill(min(intrvls_down_up[cell], intrvls_up_down[cell]),
                       max(intrvls_down_up[cell], intrvls_up_down[cell]))
        beat_num += len(measure)
        interval_list.append(measure)
        beats.append(beat_num)

    interval_line = []
    for line in interval_list:
        for interval in line:
            interval_line.append(interval)

    #  print(interval_line)

    # print(beats)

    check(interval_line, voice_names, 1, beats)
    check(interval_line, voice_names, 2, beats, 'hidden ')


soprano, alto, tenor, bass = partify(test_score)

intervalize(alto, soprano, 'soprano/alto')
intervalize(tenor, soprano, ' soprano/tenor')
intervalize(bass, soprano, 'soprano/bass')
intervalize(tenor, alto, 'alto/tenor')
intervalize(bass, alto, ' alto/bass')
intervalize(bass, tenor, 'tenor/bass')
