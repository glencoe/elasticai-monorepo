package org.ude.es.comm;

public record Posting(String topic, String data) {
    private static final String ON = "1";
    private static final String OFF = "0";

    public static Posting createTurnOn(String topic) {
        return createCommand(topic, ON);
    }

    public static Posting createTurnOff(String topic) {
        return createCommand(topic, OFF);
    }

    public static Posting createCommand(String topic, String command) {
        return new Posting(PostingType.SET.topic(topic), command);
    }

    public static Posting createStartSending(String dataId, String receiver) {
        return new Posting(PostingType.START.topic(dataId), receiver);
    }

    public static Posting createStopSending(String dataId, String receiver) {
        return new Posting(PostingType.STOP.topic(dataId), receiver);
    }

    public static Posting createData(String phenomena, String value) {
        return new Posting(PostingType.DATA.topic(phenomena), value);
    }

    public static Posting createStatus(String message) {
        return new Posting(
            PostingType.STATUS.topic(""),
            message
        );
    }

    public Posting cloneWithTopicAffix(String affix) {
        return new Posting(affix + topic(), data());
    }
}
