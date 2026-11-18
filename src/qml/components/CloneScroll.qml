import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as Controls
import org.kde.kirigami as Kirigami

Kirigami.AbstractCard {
    contentItem: Item {
        implicitWidth: delegateLayout.implicitWidth
        implicitHeight: delegateLayout.implicitHeight

        GridLayout {
            id: delegateLayout
            anchors {
                left: parent.left
                top: parent.top
                right: parent.right
            }
            Layout.bottomMargin: 20
            columns: 2

            ColumnLayout {
                Kirigami.Heading {
                    level: 4
                    text: qsTr(title)
                }

                Kirigami.Separator {
                    Layout.fillWidth: true
                }

                Kirigami.Heading {
                    level: 5
                    text: qsTr(description)
                }
            }
            Controls.CheckBox {
                Layout.alignment: Qt.AlignRight
                icon.name: "list-add-symbolic"
            }
        }
    }
}
