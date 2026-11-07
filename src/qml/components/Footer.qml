import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as Controls
import org.kde.kirigami as Kirigami

Controls.ToolBar {
	implicitHeight: Kirigami.Units.largeSpacing * 4


	RowLayout {
		anchors.fill: parent

		Item {
			Layout.fillWidth: true
		}

		Kirigami.UrlButton {
			text: qsTr("Github")
			url: "https://github.com/Ishidawg/LeShade"
		}

		Kirigami.UrlButton {
			text: qsTr("ko-fi")
			url: "https://ko-fi.com/ishidaw"
		}


		Item {
			Layout.fillWidth: true
		}
	}
}
