library ieee;
use ieee.std_logic_1164.all;

entity optical_switch is
  port (
    sel : in std_logic_vector(1 downto 0);
    i0, i1, i2, i3 : in std_logic;
    o0, o1, o2, o3 : out std_logic
  );
end entity;

architecture rtl of optical_switch is
begin
  process(sel, i0, i1, i2, i3)
  begin
    o0 <= i0;
    o1 <= i1;
    o2 <= i2;
    o3 <= i3;
    if sel = "01" then
      o0 <= i1; o1 <= i0;
    elsif sel = "10" then
      o2 <= i3; o3 <= i2;
    elsif sel = "11" then
      o0 <= i3; o1 <= i2; o2 <= i1; o3 <= i0;
    end if;
  end process;
end architecture;
