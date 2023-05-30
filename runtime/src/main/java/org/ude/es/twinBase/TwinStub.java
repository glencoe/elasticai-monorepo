package org.ude.es.twinBase;

import java.util.ArrayList;
import java.util.List;
import org.ude.es.comm.Posting;
import org.ude.es.comm.PostingType;
import org.ude.es.comm.Status;
import org.ude.es.comm.Subscriber;

public class TwinStub extends Twin {

    private final int deviceDelay;
    private boolean deviceOnline = false;

    List<DataExecutor> deviceGoesOnline = new ArrayList<>();
    List<DataExecutor> deviceGoesOffline = new ArrayList<>();

    public TwinStub(String identifier, int deviceDelay) {
        super(identifier);
        this.deviceDelay = deviceDelay;
    }

    public TwinStub(String identifier) {
        this(identifier, 0);
    }

    public void addWhenDeviceGoesOnline(DataExecutor function) {
        deviceGoesOnline.add(function);
    }

    public void addWhenDeviceGoesOffline(DataExecutor function) {
        deviceGoesOffline.add(function);
    }

    private class StatusReceiver implements Subscriber {

        String identifier;

        public StatusReceiver(String identifier) {
            this.identifier = identifier;
        }

        @Override
        public void deliver(Posting posting) throws InterruptedException {
            String data = posting.data();
            List<DataExecutor> tmpExecutor = new ArrayList<>();

            if (data.contains(Status.State.ONLINE.get())) {
                deviceOnline = true;
                tmpExecutor = new ArrayList<>(deviceGoesOnline);
            }

            if (data.contains(Status.State.OFFLINE.get())) {
                deviceOnline = false;
                tmpExecutor = new ArrayList<>(deviceGoesOffline);
            }

            for (DataExecutor executor : tmpExecutor) {
                executor.execute(posting.data());
            }
        }
    }

    @Override
    protected void executeOnBindPrivate() {
        StatusReceiver statusReceiver = new StatusReceiver(
            getDomainAndIdentifier()
        );
        subscribeForStatus(statusReceiver);
        executeOnBind();
    }

    public void waitAfterCommand() {
        try {
            Thread.sleep(deviceDelay);
        } catch (InterruptedException e) {
            throw new RuntimeException(e);
        }
    }

    public boolean isOnline() {
        return deviceOnline;
    }

    public void subscribeForData(String dataId, Subscriber subscriber) {
        this.subscribe(PostingType.DATA.topic(dataId), subscriber);
    }

    public void unsubscribeFromData(String dataId) {
        this.unsubscribe(PostingType.DATA.topic(dataId));
    }

    public void subscribeForDone(String dataId, Subscriber subscriber) {
        this.subscribe(PostingType.DONE.topic(dataId), subscriber);
    }

    public void unsubscribeFromDone(String dataId) {
        this.unsubscribe(PostingType.DONE.topic(dataId));
    }

    public void subscribeForStatus(Subscriber subscriber) {
        var topic = PostingType.STATUS.topic("");
        this.subscribe(topic, subscriber);
    }

    public void unsubscribeFromStatus() {
        var topic = PostingType.STATUS.topic("");
        this.unsubscribe(topic);
    }

    public void publishDataStartRequest(String dataId, String receiver) {
        Posting post = Posting.createStartSending(dataId, receiver);
        this.publish(post);
    }

    public void publishDataStopRequest(String dataId, String receiver) {
        Posting post = Posting.createStopSending(dataId, receiver);
        this.publish(post);
    }

    public void publishCommand(String service, String cmd) {
        Posting post = Posting.createCommand(service, cmd);
        this.publish(post);
    }
}