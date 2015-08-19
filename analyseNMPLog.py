import re

logFile = r'C:\Users\zou\Desktop\tmp\logs\multiaudio_38.fail.259964.log'
logFile = r'C:\Users\zou\Desktop\tmp\logs\tmp.log'


def plainTextChecker(line, pattern, info):
    match = re.search(pattern, line)
    if match:
        return True, info
    else:
        return False, 0


def detectProgramEnter(line):
    return plainTextChecker(line,
        'NMPMcMp2Demuxer::detectPrograms\(\) Enter',
        'detectProgram enter')


def detectProgramLeave(line):
    return plainTextChecker(line,
        'NMPMcMp2Demuxer::detectPrograms\(\) Leave',
        'detectProgram leave')


def handleDiscontinuityEnter(line):
    return plainTextChecker(line,
        'NMPMcPlayingGraph::handleDiscontinuity\(\) Enter',
        'handleDiscontinuity enter')


def handleDiscontinuityLive(line):
    return plainTextChecker(line,
        'NMPMcPlayingGraph::handleDiscontinuity\(\) Leave',
        'handleDiscontinuity leave')


def discontinuityDetected(line):
    return plainTextChecker(line,
        # 'bool ABSE::Buffer::checkDiscontinuityBySeq\(uint64_t, uint64_t\) DISCONTINUITY detected while checking',
        'ABSE::Source::read\(uint32_t, uint8_t\*, bool&, TNMPTrackType\) Detect discontinuity after read',
        'D')



def bufferRead(line):
    pattern = 'ABSE::Buffer::read\(uint32_t, uint8_t\*, bool&\) Leave : length of data read == (\d*) at sequence: (\d*)'
    match = re.search(pattern, line)
    if match:
        return True, 'read\t\t{bytesRead} at {seq}'.format(bytesRead=match.group(1), seq=match.group(2))
    else:
        return False, ''


def readout(line):
    pattern = 'ABSE::Buffer::removeFirstSegment\(\) Segment removed from buffer : (.*)/(.*\.ts)'
    match = re.search(pattern, line)
    if match:
        return True, '{ts} readout'.format(ts=match.group(2))
    else:
        return False, ''


def seek(line):
    pattern = 'ABSE::Buffer::seek\(uint64_t, bool&\) Enter seek from _readSequenceNum: (-?\d*) to xSequenceNumber: (\d*)'
    match = re.search(pattern, line)
    if match:
        return True, 'seek from {seq1} to {seq2}'.format(seq1=match.group(1), seq2=match.group(2))
    else:
        return False, ''


def setAudioTrack(line):
    # pattern = 'ABSE::Source::setAudioTrack\(ABSE::MediaMetadata\*, bool\) (.*)'
    pattern = 'ABSE::Source::setAudioTrack\(ABSE::MediaMetadata\*, bool\) (.*)/(.*\.m3u8) at sequence (-?\d*)'
    match = re.search(pattern, line)
    if match:
        return True, 'setAudioTrack to {m3u8} at {seq}'.format(m3u8=match.group(2), seq=match.group(3))
    else:
        return False, ''


def videoStreamSequence(line):
    pattern = 'ABSE::Source::onSequenceNumberChanged\(\) video stream is downloading sequence number: (\d*).  Video stream is reading sequence number: (\d*)'
    match = re.search(pattern, line)
    if match:
        return True, 'video stream downloading {seq1}, reading {seq2} '.format(seq1=match.group(1), seq2=match.group(2))
    else:
        return False, ''


def audioStreamSequence(line):
    pattern = 'ABSE::Source::onSequenceNumberChanged\(\) audio stream is downloading sequence number: (\d*).  Audio stream is reading sequence number: (\d*)'
    match = re.search(pattern, line)
    if match:
        return True, 'audio stream downloading {seq1}, reading {seq2} '.format(seq1=match.group(1), seq2=match.group(2))
    else:
        return False, ''


def requestOperation(line):
    pattern = 'Got a valid (\w*) request via requestOperation'
    match = re.search(pattern, line)
    if match:
        return True, 'requestOperation {opt}'.format(opt=match.group(1))
    else:
        return False, ''


def test(filename):
    checker = setAudioTrack
    lineNum = 0
    for l in open(filename):
        lineNum += 1
        hit, info = checker(l)
        if hit:
            print('{lineNum}\t\t{info}'.format(lineNum=lineNum, info=info))



def analyse(filename):
    # list of checkers
    checkers = [bufferRead, 
        detectProgramEnter, 
        handleDiscontinuityEnter, 
        handleDiscontinuityLive,
        readout,
        discontinuityDetected,
        seek,
        setAudioTrack,
        videoStreamSequence,
        audioStreamSequence,
        requestOperation
    ]

    # how to join info
    toMerge = [detectProgramEnter, readout, discontinuityDetected]
    toMerge = []
    lineNum = 0
    infoToMerge = []
    for l in open(filename):
        lineNum += 1
        for checker in checkers:
            hit, info = checker(l)
            if hit:
                infoToMerge.append(info)
                if checker not in toMerge:
                    print('{lineNum}\t\t{info}'.format(lineNum=lineNum, info=' | '.join(infoToMerge[::-1])))
                    infoToMerge = []


if __name__ == '__main__':
    # test(logFile)
    analyse(logFile)
