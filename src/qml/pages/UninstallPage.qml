import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as Controls
import org.kde.kirigami as Kirigami

Kirigami.Page {
	title: qsTr("LeShade - Uninstall")

	Item {
		// Container that fills the parent window, so, parent = ruler
		anchors.fill: parent

		ColumnLayout {
			// Fills horizontally only
			anchors.left: parent.left
			anchors.right: parent.right
			anchors.verticalCenter: parent.verticalCenter

			Controls.Label {
				Layout.fillWidth: true
				Layout.maximumWidth: 800
				Layout.alignment: Qt.AlignHCenter

				wrapMode: Text.WordWrap
				horizontalAlignment: Text.AlignJustify

				leftPadding: Kirigami.Units.largeSpacing * 10
				rightPadding: Kirigami.Units.largeSpacing * 10
				topPadding: Kirigami.Units.largeSpacing * 4
				bottomPadding: Kirigami.Units.largeSpacing * 2

				text: qsTr("Sexo")
			}
			RowLayout {
				Layout.alignment: Qt.AlignHCenter

				Controls.Button {
					Layout.alignment: Qt.AlignTop
					icon.name: "user-home-symbolic"
					text: qsTr("Home")

					onClicked: {
						applicationWindow().pageStack.pop()
					}
				}
				Controls.Button {
					Layout.alignment: Qt.AlignTop
					icon.name: "user-trash-symbolic"
					text: qsTr("Uninstall Selected")
				}
			}
		}
	}
}
