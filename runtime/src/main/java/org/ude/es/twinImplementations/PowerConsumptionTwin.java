package org.ude.es.twinImplementations;


import org.ude.es.comm.Posting;
import org.ude.es.comm.Subscriber;
import org.ude.es.twinBase.JavaTwin;
import org.ude.es.twinBase.TwinStub;

import java.util.ArrayList;
import java.util.List;

public class PowerConsumptionTwin extends JavaTwin {

    private final TwinStub      enV5;
    public        ValueClass    wifiValueReceiver;
    public        ValueClass    sRamValueReceiver;
    private       boolean       deviceOnline     = false;
    private final List <String> openDataRequests = new ArrayList <>( );

    private class StatusReceiver implements Subscriber {
        @Override public void deliver ( Posting posting ) {
            String data = posting.data( );
            if( data.contains( ";1" ) ) {
                deviceOnline = true;
                for( String request : openDataRequests ) {
                    enV5.publishDataStartRequest( request, identifier );
                }
            }
            openDataRequests.clear( );

            if( data.contains( ";0" ) ) {
                deviceOnline = false;
            }
        }
    }

    public PowerConsumptionTwin ( String identifier ) {
        super( identifier );

        wifiValueReceiver = new ValueClass( "wifiValue" );
        sRamValueReceiver = new ValueClass( "sRamValue" );

        enV5 = new ENv5TwinStub( "enV5" );
    }

    @Override protected void executeOnBind () {
        enV5.bindToCommunicationEndpoint( endpoint );
        StatusReceiver statusReceiver = new StatusReceiver( );
        enV5.subscribeForStatus( statusReceiver );
    }

    public class ValueClass {
        private          float         value            = -1;
        private          long          lastTimeReceived;
        private volatile boolean       receivedNewValue = false;
        private final    String        dataID;
        private final    ValueReceiver valueReceiver;
        private class ValueReceiver implements Subscriber {
            @Override public void deliver ( Posting posting ) {
                value            = Float.parseFloat( posting.data( ) );
                receivedNewValue = true;
                lastTimeReceived = System.currentTimeMillis( );
            }
        }

        public ValueClass ( String dataID ) {
            this.dataID   = dataID;
            valueReceiver = new ValueReceiver( );
        }

        public void startRequestingData () {
            if( deviceOnline ) {
                enV5.publishDataStartRequest( dataID, identifier );
                openDataRequests.add( dataID );
            } enV5.subscribeForData( dataID, valueReceiver );
        }

        public void stopRequestingData () {
            openDataRequests.remove( dataID );
            enV5.publishDataStopRequest( dataID, identifier );
            enV5.unsubscribeFromData( dataID, valueReceiver );
        }

        public float requestWifiPowerConsumptionOnce ( float timeOut ) {
            receivedNewValue = false;
            long start       = System.currentTimeMillis( );
            long timeElapsed = 0;
            startRequestingData( );
            while( !receivedNewValue && timeElapsed < timeOut ) {
                long finish = System.currentTimeMillis( );
                timeElapsed = finish - start;
            }
            stopRequestingData( );
            return value;
        }

        public boolean receivedNewValue () {
            return receivedNewValue;
        }

        public float getLastValue () {
            receivedNewValue = false;
            return value;
        }

        public long receivedWhen () {
            return lastTimeReceived;
        }
    }
}
