library ieee;
use ieee.std_logic_1164.all;

entity optical_switch_tb is
end entity;

architecture sim of optical_switch_tb is
  signal sel : std_logic_vector(1 downto 0) := "00";
  signal i0, i1, i2, i3 : std_logic := '0';
  signal o0, o1, o2, o3 : std_logic;
begin
  dut: entity work.optical_switch
    port map(sel => sel, i0 => i0, i1 => i1, i2 => i2, i3 => i3, o0 => o0, o1 => o1, o2 => o2, o3 => o3);

  stim: process
  begin
    i0 <= '1'; i1 <= '0'; i2 <= '1'; i3 <= '0';
    sel <= "00"; wait for 10 ns;
    sel <= "01"; wait for 10 ns;
    sel <= "10"; wait for 10 ns;
    sel <= "11"; wait for 10 ns;
    report "optical_switch_tb complete" severity note;
    wait;
  end process;
end architecture;
