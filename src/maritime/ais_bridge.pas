library AISBridge;

{$mode objfpc}{$H+}

uses
  Math;

function bridge_score(speed_kn: Double; sea_state: LongInt): Double; cdecl;
begin
  Result := speed_kn * (1.0 + 0.04 * sea_state) + 0.2 * Sqrt(Abs(speed_kn));
end;

exports
  bridge_score;

begin
end.
