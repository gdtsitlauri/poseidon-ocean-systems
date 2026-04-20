program AISParser;

{$mode objfpc}{$H+}

uses
  SysUtils, StrUtils, Classes, Types;

type
  TAISRecord = record
    MMSI: string;
    Latitude: string;
    Longitude: string;
    Speed: string;
    Course: string;
    VesselType: string;
  end;

function ParsePseudoAIS(const Line: string): TAISRecord;
var
  Parts: TStringDynArray;
begin
  Parts := SplitString(Line, ',');
  Result.MMSI := '0';
  Result.Latitude := '0.0';
  Result.Longitude := '0.0';
  Result.Speed := '0.0';
  Result.Course := '0.0';
  Result.VesselType := 'UNKNOWN';
  if Length(Parts) >= 12 then
  begin
    Result.MMSI := Parts[5];
    Result.Latitude := Parts[7];
    Result.Longitude := Parts[8];
    Result.Speed := Parts[9];
    Result.Course := Parts[10];
    Result.VesselType := Parts[11];
  end;
end;

var
  InLine: string;
  OutFile: TextFile;
  Rec: TAISRecord;
begin
  ForceDirectories('data');
  AssignFile(OutFile, 'data/ais_pascal_parsed.csv');
  Rewrite(OutFile);
  WriteLn(OutFile, 'mmsi,lat,lon,speed_kn,course_deg,vessel_type');
  while not EOF(Input) do
  begin
    ReadLn(InLine);
    if Pos('!AIVDM', InLine) = 1 then
    begin
      Rec := ParsePseudoAIS(InLine);
      WriteLn(OutFile, Rec.MMSI, ',', Rec.Latitude, ',', Rec.Longitude, ',', Rec.Speed, ',', Rec.Course, ',', Rec.VesselType);
    end;
  end;
  CloseFile(OutFile);
end.
