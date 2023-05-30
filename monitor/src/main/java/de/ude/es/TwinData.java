package de.ude.es;

import java.util.List;

public class TwinData {

    private final String ID;
    private String name;
    private boolean active;
    private String[] sensors;

    public TwinData(String name, String ID) {
        this.ID = ID;
        this.name = name;
        this.active = true;
        this.sensors = null;
    }

    public boolean isActive() {
        return active;
    }

    public void setActive() {
        this.active = true;
    }

    public void setInactive() {
        this.active = false;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getName() {
        return name;
    }

    public String getId() {
        return ID;
    }

    public void setAvailableSensors(String[] sensors) {
        this.sensors = sensors;
    }

    public List<String> getAvailableSensors() {
        List<String> sensorList;
        try {
            sensorList = List.of(sensors);
        } catch (Exception exception) {
            sensorList = null;
        }
        return sensorList;
    }

    public String toString() {
        return String.format("TwinData{ name='%s', ID='%s' }", name, ID);
    }
}