import { CircleMarker, MapContainer, Popup, TileLayer } from "react-leaflet";
import type { Mandi } from "../api/client";
import "leaflet/dist/leaflet.css";

type Props = { mandis: Mandi[] };

const colors: Record<Mandi["freshness"], string> = {
  FRESH: "#2f7d4a",
  STALE: "#b47b00",
  OLD: "#b34a4a",
  NO_REPORT: "#7b8178",
};

export function IndiaMap({ mandis }: Props) {
  return <MapContainer className="india-map" center={[22.5, 79]} zoom={5} scrollWheelZoom>
    <TileLayer
      attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
      url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
    />
    {mandis.map((mandi) => <CircleMarker
      center={[mandi.location.lat, mandi.location.lng]}
      pathOptions={{ color: colors[mandi.freshness], fillColor: colors[mandi.freshness], fillOpacity: 0.85 }}
      radius={9}
      key={mandi.id}
    >
      <Popup>
        <strong>{mandi.name}</strong><br />
        {mandi.district} · {mandi.freshness}<br />
        Modal price: ₹{mandi.modal_price_inr ?? "—"}
      </Popup>
    </CircleMarker>)}
  </MapContainer>;
}
