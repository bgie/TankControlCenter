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
        onTriggered: Joysticks.refresh()
    }


    Text {
        id: header
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: parent.top
        anchors.topMargin: 20
        anchors.bottomMargin: 40
        text: "Maaktank Controlecentrum"
        font.pixelSize: 64
        color: "#E0F0FF"
    }

    Row {
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: header.bottom
        anchors.bottom: parent.bottom

        Repeater {
            model: 3

            Item {
                id: gamepad
                width: parent.width / 3
                height: parent.height
                property bool connected: Joysticks.connected(index)

                Rectangle {
                    id: gamepadContent
                    anchors.fill: parent
                    anchors.margins: 20
                    color: "#FFFFFF"
                    border.color: "#000000"
                    border.width: 3
                    radius: 30

                    Rectangle  {
                        id: image
                        anchors.horizontalCenter: parent.horizontalCenter
                        anchors.bottom: player.top
                        anchors.bottomMargin: -10
                        height: 300
                        width: 450

                        Image {
                            anchors.fill: parent
                            source: "gamepad.png"
                        }
                    }

                    Text {
                        id: player
                        anchors.horizontalCenter: parent.horizontalCenter
                        anchors.bottom: debug.top
                        anchors.bottomMargin: 10
                        text: "Speler " + (index+1)
                        font.pixelSize: 64
                        color: "#000000"
                    }

                    Text {
                        id: debug
                        anchors.horizontalCenter: parent.horizontalCenter
                        anchors.bottom: parent.bottom
                        anchors.bottomMargin: 10
                    }
                }

                ColorOverlay {
                    anchors.fill: gamepadContent
                    source: gamepadContent
                    color: "#F0101010"
                    visible: !gamepad.connected
                }

                Connections {
                    target: Joysticks
                    function onRefreshed() {
                        var connected = Joysticks.connected(index);
                        gamepad.connected = connected;
                        if(connected) {
                            debug.text = Joysticks.buttons(index).toString(2) + " " +
                                Joysticks.x(index).toString() + " " +
                                Joysticks.y(index).toString();
                        }
                        else {
                            debug.text = ""
                        }
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
}
