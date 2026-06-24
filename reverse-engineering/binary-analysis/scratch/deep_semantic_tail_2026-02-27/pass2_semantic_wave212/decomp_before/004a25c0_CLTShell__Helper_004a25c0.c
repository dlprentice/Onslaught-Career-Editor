/* address: 0x004a25c0 */
/* name: CLTShell__Helper_004a25c0 */
/* signature: void __fastcall CLTShell__Helper_004a25c0(int param_1) */


void __fastcall CLTShell__Helper_004a25c0(int param_1)

{
  int iVar1;
  int *piVar2;
  undefined4 *puVar3;
  char local_190 [400];

  puVar3 = &DAT_009c2dd0;
  piVar2 = (int *)(param_1 + 0x464);
  do {
    if ((piVar2[-0x103] != piVar2[-0x81]) || (piVar2[0x83] != *piVar2)) {
      sprintf(local_190,s_Heap_Delta____32s____15d_bytes___0062f6d0);
      DebugTrace(local_190);
    }
    puVar3 = puVar3 + 8;
    piVar2 = piVar2 + 1;
  } while ((int)puVar3 < 0x9c3df0);
  puVar3 = (undefined4 *)(param_1 + 0x260);
  iVar1 = 0x81;
  do {
    *puVar3 = puVar3[-0x82];
    puVar3[0x81] = puVar3[0x104];
    puVar3 = puVar3 + 1;
    iVar1 = iVar1 + -1;
  } while (iVar1 != 0);
  return;
}
