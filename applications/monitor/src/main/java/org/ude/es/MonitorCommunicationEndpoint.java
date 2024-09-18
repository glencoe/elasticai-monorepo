package org.ude.es;

import static org.ude.es.protocol.Status.State.ONLINE;

import java.util.Arrays;
import org.ude.es.Clients.ClientList;
import org.ude.es.communicationEndpoints.LocalCommunicationEndpoint;
import org.ude.es.communicationEndpoints.RemoteCommunicationEndpoint;
import org.ude.es.protocol.Posting;
import org.ude.es.protocol.Subscriber;

public class MonitorCommunicationEndpoint extends LocalCommunicationEndpoint {

    private final ClientList clients;

    public MonitorCommunicationEndpoint(String id) {
        super(id, "MONITOR");
        this.clients = new ClientList();
    }

    @Override
    protected void executeOnBind() {
        new StatusMonitor(this, clients, this);
    }

    public ClientList getClientList() {
        return this.clients;
    }

    private static class StatusMonitor implements Subscriber {

        private final LocalCommunicationEndpoint client;
        private final ClientList clients;
        private final MonitorCommunicationEndpoint monitorCommunicationEndpoint;

        public StatusMonitor(
            LocalCommunicationEndpoint client,
            ClientList clientList,
            MonitorCommunicationEndpoint monitorCommunicationEndpoint
        ) {
            System.out.println("StatusMonitor");
            this.clients = clientList;
            this.client = client;
            this.monitorCommunicationEndpoint = monitorCommunicationEndpoint;
            createTwinStubAndSubscribeForStatus();
        }

        private void createTwinStubAndSubscribeForStatus() {
            System.out.println("Creating TwinStubAndSubscribeForStatus");
            RemoteCommunicationEndpoint stub = new RemoteCommunicationEndpoint("+");
            stub.bindToCommunicationEndpoint(this.client.getBroker());
            stub.subscribeForStatus(this);
        }

        @Override
        public void deliver(Posting posting) {
            String twinID = posting
                .data()
                .substring(posting.data().indexOf("ID") + ("ID").length() + 1);
            twinID = twinID.substring(0, twinID.indexOf(";"));

            String twinIDFromTopic = posting
                .topic()
                .split("/")[Arrays.asList(posting.topic().split("/")).indexOf("STATUS") - 1];

            if (!twinID.equals(twinIDFromTopic)) {
                System.out.printf(
                    "Topic ID '%s' and ID '%s' in Status differ! Ignoring!%n",
                    twinIDFromTopic,
                    twinID
                );
                return;
            }

            boolean twinActive = posting.data().contains(ONLINE.toString());

            //            System.out.printf(
            //                "Client with ID '%s' online: %b.%n",
            //                twinID,
            //                twinActive
            //            );

            clients.addOrUpdateClient(
                twinID,
                posting.data(),
                monitorCommunicationEndpoint.getBroker()
            );
        }
    }
}
