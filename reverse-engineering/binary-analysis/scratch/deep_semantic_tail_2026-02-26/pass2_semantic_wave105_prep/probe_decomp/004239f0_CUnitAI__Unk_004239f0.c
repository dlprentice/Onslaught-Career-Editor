/* address: 0x004239f0 */
/* name: CUnitAI__Unk_004239f0 */
/* signature: int __fastcall CUnitAI__Unk_004239f0(void * param_1) */


int __fastcall CUnitAI__Unk_004239f0(void *param_1)

{
  char cVar1;
  uint uVar2;
  uint uVar3;
  char *pcVar4;
  char *pcVar5;

  *(undefined1 *)((int)param_1 + 0x17d) = 0;
  *(undefined1 *)((int)param_1 + 0x182) = 0;
  *(undefined1 *)((int)param_1 + 0x183) = 0;
  *(undefined4 *)param_1 = 1;
  *(undefined4 *)((int)param_1 + 0x14) = 1;
  *(undefined4 *)((int)param_1 + 0x2ac) = 1;
  *(undefined4 *)((int)param_1 + 0x1c) = 0;
  *(undefined4 *)((int)param_1 + 0x20) = 0;
  *(undefined4 *)((int)param_1 + 0x24) = 0;
  *(undefined4 *)((int)param_1 + 0x28) = 0;
  *(undefined4 *)((int)param_1 + 0x18) = 0;
  *(undefined4 *)((int)param_1 + 8) = 0;
  *(undefined4 *)((int)param_1 + 0x16c) = 0;
  *(undefined1 *)((int)param_1 + 0x185) = 0;
  *(undefined4 *)((int)param_1 + 0x30) = 0;
  *(undefined4 *)((int)param_1 + 0x2c) = 0;
  *(undefined1 *)((int)param_1 + 0x180) = 0;
  *(undefined4 *)((int)param_1 + 0x2a8) = 0;
  uVar2 = 0xffffffff;
  *(undefined4 *)((int)param_1 + 0x3c) = 0;
  pcVar4 = s_c__beaautoconfigtest__00624488;
  do {
    pcVar5 = pcVar4;
    if (uVar2 == 0) break;
    uVar2 = uVar2 - 1;
    pcVar5 = pcVar4 + 1;
    cVar1 = *pcVar4;
    pcVar4 = pcVar5;
  } while (cVar1 != '\0');
  uVar2 = ~uVar2;
  pcVar4 = pcVar5 + -uVar2;
  pcVar5 = (char *)((int)param_1 + 0x44);
  for (uVar3 = uVar2 >> 2; uVar3 != 0; uVar3 = uVar3 - 1) {
    *(undefined4 *)pcVar5 = *(undefined4 *)pcVar4;
    pcVar4 = pcVar4 + 4;
    pcVar5 = pcVar5 + 4;
  }
  for (uVar2 = uVar2 & 3; uVar2 != 0; uVar2 = uVar2 - 1) {
    *pcVar5 = *pcVar4;
    pcVar4 = pcVar4 + 1;
    pcVar5 = pcVar5 + 1;
  }
  *(undefined4 *)((int)param_1 + 0x34) = 0;
  *(undefined4 *)((int)param_1 + 0x148) = 0;
  *(undefined4 *)((int)param_1 + 0x40) = 1;
  *(undefined4 *)((int)param_1 + 0x154) = 0;
  *(undefined4 *)((int)param_1 + 0x158) = 0;
  *(undefined4 *)((int)param_1 + 0x15c) = 0;
  *(undefined4 *)((int)param_1 + 0x188) = 1;
  *(undefined4 *)((int)param_1 + 0x18c) = 0;
  *(undefined4 *)((int)param_1 + 0x150) = 0;
  uVar2 = 0xffffffff;
  *(undefined4 *)((int)param_1 + 0x2b8) = 0;
  *(undefined4 *)((int)param_1 + 700) = 0;
  *(undefined1 *)((int)param_1 + 0x184) = 0;
  *(undefined4 *)((int)param_1 + 0x2c4) = 1;
  *(undefined4 *)((int)param_1 + 0x2c8) = 1;
  *(undefined4 *)((int)param_1 + 0x2cc) = 0xffffffff;
  *(undefined4 *)((int)param_1 + 0x2d0) = 0xffffffff;
  *(undefined1 *)((int)param_1 + 0x186) = 0;
  *(undefined4 *)((int)param_1 + 0x2c0) = 0;
  *(undefined4 *)((int)param_1 + 0x2b4) = 1;
  *(undefined1 *)((int)param_1 + 0x181) = 0;
  *(undefined4 *)((int)param_1 + 0x160) = 0x7fffffff;
  *(undefined4 *)((int)param_1 + 0x38) = 0;
  *(undefined4 *)((int)param_1 + 0x178) = 0;
  *(undefined4 *)((int)param_1 + 0x2a0) = 0;
  *(undefined4 *)((int)param_1 + 0x2b0) = 0;
  *(undefined4 *)((int)param_1 + 400) = 0;
  *(undefined4 *)((int)param_1 + 4) = 0;
  *(undefined4 *)((int)param_1 + 0x10) = 0xffffffff;
  *(undefined1 *)((int)param_1 + 0x17c) = 0;
  *(undefined1 *)((int)param_1 + 0x17e) = 0;
  *(undefined4 *)((int)param_1 + 0xc) = 0;
  *(undefined4 *)((int)param_1 + 0x170) = 1;
  *(undefined4 *)((int)param_1 + 0x294) = 0xffffffff;
  *(undefined1 *)((int)param_1 + 0x17f) = 1;
  *(undefined4 *)((int)param_1 + 0x2a4) = 0;
  *(undefined4 *)((int)param_1 + 0x174) = 0;
  *(undefined4 *)((int)param_1 + 0x29c) = 0;
  pcVar4 = &DAT_00624484;
  do {
    pcVar5 = pcVar4;
    if (uVar2 == 0) break;
    uVar2 = uVar2 - 1;
    pcVar5 = pcVar4 + 1;
    cVar1 = *pcVar4;
    pcVar4 = pcVar5;
  } while (cVar1 != '\0');
  uVar2 = ~uVar2;
  pcVar4 = pcVar5 + -uVar2;
  pcVar5 = (char *)((int)param_1 + 0x2d4);
  for (uVar3 = uVar2 >> 2; uVar3 != 0; uVar3 = uVar3 - 1) {
    *(undefined4 *)pcVar5 = *(undefined4 *)pcVar4;
    pcVar4 = pcVar4 + 4;
    pcVar5 = pcVar5 + 4;
  }
  for (uVar2 = uVar2 & 3; uVar2 != 0; uVar2 = uVar2 - 1) {
    *pcVar5 = *pcVar4;
    pcVar4 = pcVar4 + 1;
    pcVar5 = pcVar5 + 1;
  }
  *(undefined4 *)((int)param_1 + 0x314) = 0;
  if (DAT_0066e94e == '\0') {
    *(undefined4 *)((int)param_1 + 0x318) = 0xffffffff;
  }
  else {
    *(undefined4 *)((int)param_1 + 0x318) = 120000;
  }
  *(undefined4 *)((int)param_1 + 0x14c) = 1;
  *(undefined4 *)((int)param_1 + 0x298) = 0;
  *(undefined4 *)((int)param_1 + 0x31c) = 0xffffffff;
  return (int)param_1;
}
