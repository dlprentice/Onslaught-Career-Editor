/* address: 0x00592530 */
/* name: CFastVB__JpegParser_ReadAndValidateSOI */
/* signature: int __stdcall CFastVB__JpegParser_ReadAndValidateSOI(void * param_1) */


int CFastVB__JpegParser_ReadAndValidateSOI(void *param_1)

{
  byte bVar1;
  undefined4 *puVar2;
  undefined4 *puVar3;
  int iVar4;
  uint uVar5;
  byte *pbVar6;
  uint unaff_retaddr;

  puVar2 = *(undefined4 **)((int)param_1 + 0x18);
  pbVar6 = (byte *)*puVar2;
  iVar4 = puVar2[1];
  if (iVar4 == 0) {
    iVar4 = (*(code *)puVar2[3])(param_1);
    if (iVar4 == 0) {
      return 0;
    }
    pbVar6 = (byte *)*puVar2;
    iVar4 = puVar2[1];
  }
  bVar1 = *pbVar6;
  iVar4 = iVar4 + -1;
  pbVar6 = pbVar6 + 1;
  if (iVar4 == 0) {
    iVar4 = (*(code *)puVar2[3])(param_1);
    if (iVar4 == 0) {
      return 0;
    }
    pbVar6 = (byte *)*puVar2;
    iVar4 = puVar2[1];
  }
  uVar5 = (uint)*pbVar6;
  if ((bVar1 != 0xff) || (uVar5 != 0xd8)) {
    puVar3 = *(undefined4 **)param_1;
    puVar3[5] = 0x35;
    puVar3[6] = (uint)bVar1;
    puVar3[7] = uVar5;
    (*(code *)*puVar3)(param_1);
    uVar5 = unaff_retaddr;
  }
  puVar2[1] = iVar4 + -1;
  *puVar2 = pbVar6 + 1;
  *(uint *)((int)param_1 + 0x1a4) = uVar5;
  return 1;
}
