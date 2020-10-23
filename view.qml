import QtQuick 2.12
import QtQuick.Layouts 1.12
import QtQuick.Controls 2.12
import QtQuick.Window 2.12
import QtGraphicalEffects 1.12

ApplicationWindow {
    id: window
    title: header.text
    width: 1200
    height: 800
    visible: true
    visibility: Qt.WindowFullScreen
    flags: Qt.FramelessWindowHint | Qt.Window

    background: Rectangle {
        color:  "#101010"
    }

    Timer {
        interval: 1;
        running: true;
        repeat: true
        onTriggered: {
            Joysticks.refresh();
            RemoteControl.discover();
        }
    }


    Text {
        id: header
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: parent.top
        anchors.topMargin: 20
        anchors.bottomMargin: 40
        text: "Controle Centrum"
        font.pixelSize: 64
        color: "#E0F0FF"
    }

    Item {
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: header.bottom
        anchors.bottom: parent.bottom

        Grid {
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            height: parent.height

            columns: 2
            rows: 2

            Repeater {
                model: Tanks

                Item {
                    id: tankItem
                    width: parent.width / parent.columns
                    height: parent.height / parent.rows

                    Rectangle {
                        id: tankContent
                        anchors.fill: parent
                        anchors.margins: 20
                        color: "#DBD2CD"
                        border.color: "#000000"
                        border.width: 3
                        radius: 30

                        Rectangle  {
                            id: tankImage
                            anchors.centerIn: parent
                            width: 1000 / 2
                            height: 718 / 2

                            Image {
                                anchors.fill: parent
                                source: "tank.png"
                            }
                        }

                        Text {
                            anchors.horizontalCenter: parent.horizontalCenter
                            anchors.top: parent.top
                            anchors.topMargin: 20
                            text: modelData.name
                            font.pixelSize: 48
                            color: "#000000"
                        }
                    }

                    ColorOverlay {
                        anchors.fill: tankContent
                        source: tankContent
                        color: "#F0101010"
                        visible: !modelData.connected
                    }
                }
            }
        }
    }

    Button {
        id: closeButton
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.margins: 20
        width: 32
        height: 32
        background: Item {}
        onClicked: window.close()

        Image {
            visible: closeButton.hovered
            anchors.fill: parent
            source: "close-button.png"
        }
        Image {
            visible: !closeButton.hovered
            anchors.fill: parent
            source: "close-button-grayed.png"
        }
    }

    Text {
        id: refreshesPerSecond
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        anchors.margins: 5
        color: "#707070"

        Timer {
            interval: 1000;
            running: true;
            repeat: true
            onTriggered: refreshesPerSecond.text = "Joystick latency: " + (1000 / Joysticks.refreshesPerSecond()).toFixed(2) + "ms"
        }
    }
}
