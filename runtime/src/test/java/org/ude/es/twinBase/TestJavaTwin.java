package org.ude.es.twinBase;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.ude.es.Checker;
import org.ude.es.comm.Posting;
import org.ude.es.comm.PostingType;
import org.ude.es.comm.Status;

public class TestJavaTwin {

    private static final String twinID = "test";

    private static class JavaTwinChecker extends Checker {

        public JavaTwin device;

        public void givenDevice() {
            device = new JavaTwin(twinID);
            device.bindToCommunicationEndpoint(broker);
        }

        public void whenPublishingData(String dataId, String value) {
            String topic =
                device.getDomainAndIdentifier() +
                PostingType.DATA.topic(dataId);
            expected = new Posting(topic, value);
            device.publishData(dataId, value);
        }

        public void whenPublishingDone(String dataId, String value) {
            String topic =
                device.getDomainAndIdentifier() +
                PostingType.DONE.topic(dataId);
            expected = new Posting(topic, value);
            device.publishDone(dataId, value);
        }

        public void whenPublishingStatus() {
            String topic =
                device.getDomainAndIdentifier() + PostingType.STATUS.topic("");
            expected =
                new Posting(
                    topic,
                    "ID:" + device.identifier + ";TYPE:TWIN;STATE:ONLINE;"
                );
            device.publishStatus(
                new Status(device.getIdentifier())
                    .append(Status.Parameter.TYPE.value(Status.Type.TWIN.get()))
                    .append(
                        Status.Parameter.STATE.value(Status.State.ONLINE.get())
                    )
            );
        }

        public void whenSubscribingForDataStart(String dataId) {
            device.subscribeForDataStartRequest(dataId, subscriber);
        }

        public void whenUnsubscribingFromDataStart(String dataId) {
            device.unsubscribeFromDataStartRequest(dataId);
        }

        public void whenSubscribingForDataStop(String dataId) {
            device.subscribeForDataStopRequest(dataId, subscriber);
        }

        public void whenUnsubscribingFromDataStop(String dataId) {
            device.unsubscribeFromDataStopRequest(dataId);
        }

        public void whenSubscribingForCommand(String dataId) {
            device.subscribeForCommand(dataId, subscriber);
        }

        public void whenUnsubscribingFromCommand(String dataId) {
            device.unsubscribeFromCommand(dataId);
        }
    }

    private JavaTwinChecker checker;

    @BeforeEach
    public void setUp() {
        checker = new JavaTwinChecker();
        checker.givenBroker();
        checker.givenDevice();
    }

    @Test
    void weCanPublishData() {
        checker.givenSubscriptionAtBrokerFor(twinID + "/DATA/temperature");
        checker.whenPublishingData("temperature", "13.5");
        checker.thenPostingIsDelivered();
    }

    @Test
    void weCanPublishStatus() {
        checker.givenSubscriptionAtBrokerFor(twinID + "/STATUS");
        checker.whenPublishingStatus();
        checker.thenPostingIsDelivered();
    }

    @Test
    void weCanPublishDone() {
        checker.givenSubscriptionAtBrokerFor(twinID + "/DONE/cmd");
        checker.whenPublishingDone("cmd", "test");
        checker.thenPostingIsDelivered();
    }

    @Test
    void weCanSubscribeForDataStartRequest() {
        checker.whenSubscribingForDataStart("data");
        checker.whenPostingIsPublishedAtBroker(twinID + "/START/data", twinID);
        checker.thenPostingIsDelivered();
    }

    @Test
    void weCanUnsubscribeFromDataStartRequest() {
        checker.whenSubscribingForDataStart("data");
        checker.whenUnsubscribingFromDataStart("data");
        checker.whenPostingIsPublishedAtBroker(twinID + "/START/data", twinID);
        checker.thenPostingIsNotDelivered();
    }

    @Test
    void weCanSubscribeForDataStopRequest() {
        checker.whenSubscribingForDataStop("data");
        checker.whenPostingIsPublishedAtBroker(twinID + "/STOP/data", twinID);
        checker.thenPostingIsDelivered();
    }

    @Test
    void weCanUnsubscribeFromDataStopRequest() {
        checker.whenSubscribingForDataStop("data");
        checker.whenUnsubscribingFromDataStop("data");
        checker.whenPostingIsPublishedAtBroker(twinID + "/STOP/data", twinID);
        checker.thenPostingIsNotDelivered();
    }

    @Test
    void weCanSubscribeForCommand() {
        checker.whenSubscribingForCommand("cmd");
        checker.whenPostingIsPublishedAtBroker(twinID + "/DO/cmd", twinID);
        checker.thenPostingIsDelivered();
    }

    @Test
    void weCanUnsubscribeFromCommand() {
        checker.whenSubscribingForCommand("data");
        checker.whenUnsubscribingFromCommand("data");
        checker.whenPostingIsPublishedAtBroker(twinID + "/SET/data", twinID);
        checker.thenPostingIsNotDelivered();
    }
}