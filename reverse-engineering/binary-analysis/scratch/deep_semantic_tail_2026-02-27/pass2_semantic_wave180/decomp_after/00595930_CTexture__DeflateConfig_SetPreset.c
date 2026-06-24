/* address: 0x00595930 */
/* name: CTexture__DeflateConfig_SetPreset */
/* signature: void __stdcall CTexture__DeflateConfig_SetPreset(void * param_1, int param_2) */


void CTexture__DeflateConfig_SetPreset(void *param_1,int param_2)

{
  int iVar1;
  undefined4 *puVar2;
  int iVar3;
  int *piVar4;

  iVar1 = *(int *)((int)param_1 + 0x14);
  if (iVar1 != 100) {
    puVar2 = *(undefined4 **)param_1;
    puVar2[5] = 0x14;
    puVar2[6] = iVar1;
    (*(code *)*puVar2)(param_1);
  }
  *(int *)((int)param_1 + 0x40) = param_2;
  *(undefined4 *)((int)param_1 + 0xd0) = 0;
  *(undefined4 *)((int)param_1 + 0xdc) = 0;
  *(undefined4 *)((int)param_1 + 0xe0) = 1;
  *(undefined4 *)((int)param_1 + 0xe4) = 1;
  switch(param_2) {
  case 0:
    iVar1 = *(int *)((int)param_1 + 0x24);
    *(int *)((int)param_1 + 0x3c) = iVar1;
    if ((iVar1 < 1) || (10 < iVar1)) {
      puVar2 = *(undefined4 **)param_1;
      puVar2[5] = 0x1a;
      puVar2[6] = iVar1;
      puVar2[7] = 10;
      (*(code *)*puVar2)(param_1);
    }
    iVar1 = *(int *)((int)param_1 + 0x3c);
    iVar3 = 0;
    if (0 < iVar1) {
      piVar4 = *(int **)((int)param_1 + 0x44);
      do {
        *piVar4 = iVar3;
        piVar4[2] = 1;
        piVar4[3] = 1;
        piVar4[4] = 0;
        piVar4[5] = 0;
        piVar4[6] = 0;
        iVar3 = iVar3 + 1;
        piVar4 = piVar4 + 0x15;
      } while (iVar3 < iVar1);
      return;
    }
    break;
  case 1:
    *(undefined4 *)((int)param_1 + 0xd0) = 1;
    *(undefined4 *)((int)param_1 + 0x3c) = 1;
    puVar2 = *(undefined4 **)((int)param_1 + 0x44);
    *puVar2 = 1;
    puVar2[2] = 1;
    puVar2[3] = 1;
    puVar2[4] = 0;
    puVar2[5] = 0;
    puVar2[6] = 0;
    return;
  case 2:
    *(undefined4 *)((int)param_1 + 0xdc) = 1;
    *(undefined4 *)((int)param_1 + 0x3c) = 3;
    puVar2 = *(undefined4 **)((int)param_1 + 0x44);
    puVar2[2] = 1;
    puVar2[3] = 1;
    puVar2[4] = 0;
    puVar2[5] = 0;
    puVar2[6] = 0;
    *puVar2 = 0x52;
    puVar2[0x17] = 1;
    puVar2[0x18] = 1;
    puVar2[0x19] = 0;
    puVar2[0x1a] = 0;
    puVar2[0x1b] = 0;
    puVar2[0x15] = 0x47;
    puVar2[0x2c] = 1;
    puVar2[0x2d] = 1;
    puVar2[0x2e] = 0;
    puVar2[0x2f] = 0;
    puVar2[0x30] = 0;
    puVar2[0x2a] = 0x42;
    return;
  case 3:
    *(undefined4 *)((int)param_1 + 0xd0) = 1;
    *(undefined4 *)((int)param_1 + 0x3c) = 3;
    puVar2 = *(undefined4 **)((int)param_1 + 0x44);
    *puVar2 = 1;
    puVar2[4] = 0;
    puVar2[5] = 0;
    puVar2[6] = 0;
    puVar2[2] = 2;
    puVar2[3] = 2;
    puVar2[0x17] = 1;
    puVar2[0x18] = 1;
    puVar2[0x19] = 1;
    puVar2[0x1a] = 1;
    puVar2[0x1b] = 1;
    puVar2[0x15] = 2;
    puVar2[0x2c] = 1;
    puVar2[0x2d] = 1;
    puVar2[0x2e] = 1;
    puVar2[0x2f] = 1;
    puVar2[0x30] = 1;
    puVar2[0x2a] = 3;
    return;
  case 4:
    *(undefined4 *)((int)param_1 + 0xdc) = 1;
    *(undefined4 *)((int)param_1 + 0x3c) = 4;
    puVar2 = *(undefined4 **)((int)param_1 + 0x44);
    puVar2[2] = 1;
    puVar2[3] = 1;
    puVar2[4] = 0;
    puVar2[5] = 0;
    puVar2[6] = 0;
    *puVar2 = 0x43;
    puVar2[0x17] = 1;
    puVar2[0x18] = 1;
    puVar2[0x19] = 0;
    puVar2[0x1a] = 0;
    puVar2[0x1b] = 0;
    puVar2[0x15] = 0x4d;
    puVar2[0x2c] = 1;
    puVar2[0x2d] = 1;
    puVar2[0x2e] = 0;
    puVar2[0x2f] = 0;
    puVar2[0x30] = 0;
    puVar2[0x2a] = 0x59;
    puVar2[0x41] = 1;
    puVar2[0x42] = 1;
    puVar2[0x43] = 0;
    puVar2[0x44] = 0;
    puVar2[0x45] = 0;
    puVar2[0x3f] = 0x4b;
    return;
  case 5:
    puVar2 = *(undefined4 **)((int)param_1 + 0x44);
    *puVar2 = 1;
    puVar2[4] = 0;
    puVar2[5] = 0;
    puVar2[6] = 0;
    puVar2[2] = 2;
    puVar2[3] = 2;
    puVar2[0x17] = 1;
    puVar2[0x18] = 1;
    puVar2[0x19] = 1;
    puVar2[0x1a] = 1;
    puVar2[0x1b] = 1;
    puVar2[0x15] = 2;
    puVar2[0x2c] = 1;
    puVar2[0x2d] = 1;
    puVar2[0x2e] = 1;
    puVar2[0x2f] = 1;
    puVar2[0x30] = 1;
    puVar2[0x2a] = 3;
    *(undefined4 *)((int)param_1 + 0xdc) = 1;
    *(undefined4 *)((int)param_1 + 0x3c) = 4;
    puVar2[0x43] = 0;
    puVar2[0x44] = 0;
    puVar2[0x45] = 0;
    puVar2[0x3f] = 4;
    puVar2[0x41] = 2;
    puVar2[0x42] = 2;
    return;
  default:
    puVar2 = *(undefined4 **)param_1;
    puVar2[5] = 10;
    (*(code *)*puVar2)(param_1);
  }
  return;
}
