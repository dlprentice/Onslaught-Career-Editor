/* address: 0x004422d0 */
/* name: CSoundManager__Helper_004422d0 */
/* signature: int __fastcall CSoundManager__Helper_004422d0(void * param_1) */


int __fastcall CSoundManager__Helper_004422d0(void *param_1)

{
  char cVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  undefined4 *puVar5;
  char *pcVar6;
  undefined4 *puVar7;
  char *pcVar8;

  *(void **)param_1 = DAT_0066ffb0;
  DAT_0066ffb0 = param_1;
  *(undefined4 *)((int)param_1 + 4) = 0;
  *(undefined4 *)((int)param_1 + 8) = 0;
  *(undefined4 *)((int)param_1 + 0xc) = 0;
  *(undefined4 *)((int)param_1 + 0x84) = 0x3f000000;
  *(undefined4 *)((int)param_1 + 0x88) = 0x3f000000;
  *(undefined4 *)((int)param_1 + 0x8c) = 0x3f000000;
  puVar5 = &DAT_0066ff80;
  puVar7 = (undefined4 *)((int)param_1 + 0x14);
  for (iVar2 = 0xc; iVar2 != 0; iVar2 = iVar2 + -1) {
    *puVar7 = *puVar5;
    puVar5 = puVar5 + 1;
    puVar7 = puVar7 + 1;
  }
  *(undefined4 *)((int)param_1 + 0x94) = 0xffffffff;
  *(undefined4 *)((int)param_1 + 0x44) = DAT_0066ffb8;
  *(undefined4 *)((int)param_1 + 0x48) = DAT_0066ffbc;
  *(undefined4 *)((int)param_1 + 0x4c) = DAT_0066ffc0;
  *(undefined4 *)((int)param_1 + 0x50) = DAT_0066ffc4;
  puVar5 = &DAT_0066ff80;
  puVar7 = (undefined4 *)((int)param_1 + 0x54);
  for (iVar2 = 0xc; iVar2 != 0; iVar2 = iVar2 + -1) {
    *puVar7 = *puVar5;
    puVar5 = puVar5 + 1;
    puVar7 = puVar7 + 1;
  }
  uVar3 = 0xffffffff;
  pcVar6 = &DAT_00662b2c;
  do {
    pcVar8 = pcVar6;
    if (uVar3 == 0) break;
    uVar3 = uVar3 - 1;
    pcVar8 = pcVar6 + 1;
    cVar1 = *pcVar6;
    pcVar6 = pcVar8;
  } while (cVar1 != '\0');
  uVar3 = ~uVar3;
  pcVar6 = pcVar8 + -uVar3;
  pcVar8 = (char *)((int)param_1 + 0x98);
  for (uVar4 = uVar3 >> 2; uVar4 != 0; uVar4 = uVar4 - 1) {
    *(undefined4 *)pcVar8 = *(undefined4 *)pcVar6;
    pcVar6 = pcVar6 + 4;
    pcVar8 = pcVar8 + 4;
  }
  for (uVar3 = uVar3 & 3; uVar3 != 0; uVar3 = uVar3 - 1) {
    *pcVar8 = *pcVar6;
    pcVar6 = pcVar6 + 1;
    pcVar8 = pcVar8 + 1;
  }
  return (int)param_1;
}
