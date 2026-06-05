import cv2


def extrahiere_frame(video_pfad, frame_nummer, ausgabe_pfad):
    # Video öffnen
    cap = cv2.VideoCapture(video_pfad)

    # Zur gewünschten Frame-Nummer springen
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_nummer)

    # Frame lesen
    erfolg, frame = cap.read()

    if erfolg:
        # Als PNG speichern (verlustfrei)
        cv2.imwrite(ausgabe_pfad, frame)
        print(f"Frame {frame_nummer} erfolgreich gespeichert unter: {ausgabe_pfad}")
    else:
        print("Fehler: Frame konnte nicht gelesen werden.")

    cap.release()


# Beispielaufruf
extrahiere_frame('./video/Video44.mp4', 120, 'frame_analyse.png')