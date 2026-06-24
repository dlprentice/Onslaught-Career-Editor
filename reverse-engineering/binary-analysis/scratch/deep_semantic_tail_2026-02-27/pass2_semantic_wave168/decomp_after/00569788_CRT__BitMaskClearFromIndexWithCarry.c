/* address: 0x00569788 */
/* name: CRT__BitMaskClearFromIndexWithCarry */
/* signature: int __cdecl CRT__BitMaskClearFromIndexWithCarry(int param_1, int param_2) */


int __cdecl CRT__BitMaskClearFromIndexWithCarry(int param_1,int param_2)

{
  uint *puVar1;
  int iVar2;
  int extraout_EAX;
  byte bVar3;
  int iVar4;
  undefined4 *puVar5;
  int local_8;

  local_8 = 0;
  puVar1 = (uint *)(param_1 + (param_2 / 0x20) * 4);
  bVar3 = 0x1f - (char)(param_2 % 0x20);
  if (((*puVar1 & 1 << (bVar3 & 0x1f)) != 0) &&
     (iVar2 = CRT__AreHigherMaskBitsClear(param_1,param_2 + 1), iVar2 == 0)) {
    CRT__PropagateMaskCarryBackward(param_1,param_2 + -1);
    local_8 = extraout_EAX;
  }
  *puVar1 = *puVar1 & -1 << (bVar3 & 0x1f);
  iVar2 = param_2 / 0x20 + 1;
  if (iVar2 < 3) {
    puVar5 = (undefined4 *)(param_1 + iVar2 * 4);
    for (iVar4 = 3 - iVar2; iVar4 != 0; iVar4 = iVar4 + -1) {
      *puVar5 = 0;
      puVar5 = puVar5 + 1;
    }
  }
  return local_8;
}
