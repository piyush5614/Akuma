import { useEffect } from "react";
import { DivIcon } from "leaflet";
import { CircleMarker, MapContainer, Marker, Polyline, Popup, TileLayer, useMap } from "react-leaflet";
import type { Mandi } from "../api/client";
import "leaflet/dist/leaflet.css";

type Props = { mandis: Mandi[]; farmerLocation?: { lat: number; lng: number }; selectedId?: string; onSelect?: (mandiId: string) => void };

function FitMandis({ mandis, farmerLocation }: Pick<Props, "mandis" | "farmerLocation">) {
  const map = useMap();
  useEffect(() => {
    const points: [number, number][] = mandis.slice(0, 5).map((mandi) => [mandi.location.lat, mandi.location.lng]);
    if (farmerLocation) points.push([farmerLocation.lat, farmerLocation.lng]);
    if (points.length === 1) map.setView(points[0], 10);
    else if (points.length > 1) map.fitBounds(points, { padding: [48, 48], maxZoom: 12 });
  }, [mandis, farmerLocation, map]);
  return null;
}

export function IndiaMap({ mandis, farmerLocation, selectedId, onSelect }: Props) {
  const selected = mandis.find((mandi) => mandi.id === selectedId);
  return <MapContainer className="india-map" center={farmerLocation ? [farmerLocation.lat, farmerLocation.lng] : [22.5, 79]} zoom={farmerLocation ? 9 : 5} scrollWheelZoom>
    <TileLayer
      attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
      url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
    />
    <FitMandis mandis={mandis} farmerLocation={farmerLocation} />
    {farmerLocation && <>
      <CircleMarker center={[farmerLocation.lat, farmerLocation.lng]} pathOptions={{ color: "#1f62dc", fillColor: "#1f62dc", fillOpacity: 0.14 }} radius={22} />
      <Marker position={[farmerLocation.lat, farmerLocation.lng]} icon={new DivIcon({ className: "you-marker-icon", html: '<span class="you-marker"><span></span>You</span>', iconSize: [48, 48], iconAnchor: [24, 24] })}>
        <Popup><strong>Your location</strong></Popup>
      </Marker>
    </>}
    {selected && farmerLocation && <Polyline positions={[[farmerLocation.lat, farmerLocation.lng], [selected.location.lat, selected.location.lng]]} pathOptions={{ color: "#1f62dc", weight: 2, dashArray: "7 8", opacity: 0.8 }} />}
    {mandis.slice(0, 40).map((mandi, index) => {
      const rank = index + 1;
      const icon = new DivIcon({
        className: "price-marker-icon",
        html: `<span class="price-marker ${mandi.freshness.toLowerCase()} ${selectedId === mandi.id ? "selected" : ""}"><b>${rank}</b><strong>${mandi.modal_price_inr ? `₹${Number(mandi.modal_price_inr).toLocaleString("en-IN")}/q` : mandi.name}</strong></span>`,
        iconSize: [116, 38],
        iconAnchor: [58, 38],
      });
      return <Marker
        position={[mandi.location.lat, mandi.location.lng]}
        icon={icon}
        key={mandi.id}
        eventHandlers={{ click: () => onSelect?.(mandi.id) }}
      >
        <Popup>
          <strong>{mandi.name}</strong><br />
          {mandi.district} · {mandi.freshness}<br />
          Modal price: ₹{mandi.modal_price_inr ?? "—"}
        </Popup>
      </Marker>;
    })}
  </MapContainer>;
}
