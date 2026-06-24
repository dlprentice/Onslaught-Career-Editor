/* address: 0x00595c10 */
/* name: CTexture__ConfigureDeflatePresetByCompressionMode */
/* signature: void __stdcall CTexture__ConfigureDeflatePresetByCompressionMode(void * param_1) */


void CTexture__ConfigureDeflatePresetByCompressionMode(void *param_1)

{
  int iVar1;
  undefined4 *puVar2;

  switch(*(undefined4 *)((int)param_1 + 0x28)) {
  case 0:
    CTexture__DeflateConfig_SetPreset(param_1,0);
    return;
  case 1:
  case 8:
    iVar1 = *(int *)((int)param_1 + 0x14);
    if (iVar1 != 100) {
      puVar2 = *(undefined4 **)param_1;
      puVar2[5] = 0x14;
      puVar2[6] = iVar1;
      (*(code *)*puVar2)(param_1);
    }
    break;
  case 2:
  case 3:
  case 6:
  case 7:
    CTexture__DeflateConfig_SetPreset(param_1,3);
    return;
  case 4:
    CTexture__DeflateConfig_SetPreset(param_1,4);
    return;
  case 5:
    iVar1 = *(int *)((int)param_1 + 0x14);
    if (iVar1 != 100) {
      puVar2 = *(undefined4 **)param_1;
      puVar2[5] = 0x14;
      puVar2[6] = iVar1;
      (*(code *)*puVar2)(param_1);
    }
    puVar2 = *(undefined4 **)((int)param_1 + 0x44);
    *puVar2 = 1;
    puVar2[4] = 0;
    puVar2[5] = 0;
    puVar2[6] = 0;
    *(undefined4 *)((int)param_1 + 0x40) = 5;
    *(undefined4 *)((int)param_1 + 0xd0) = 0;
    *(undefined4 *)((int)param_1 + 0xe0) = 1;
    *(undefined4 *)((int)param_1 + 0xe4) = 1;
    *(undefined4 *)((int)param_1 + 0xdc) = 1;
    *(undefined4 *)((int)param_1 + 0x3c) = 4;
    puVar2[2] = 2;
    puVar2[3] = 2;
    puVar2[0x15] = 2;
    puVar2[0x17] = 1;
    puVar2[0x18] = 1;
    puVar2[0x19] = 1;
    puVar2[0x1a] = 1;
    puVar2[0x1b] = 1;
    puVar2[0x2a] = 3;
    puVar2[0x2c] = 1;
    puVar2[0x2d] = 1;
    puVar2[0x2e] = 1;
    puVar2[0x2f] = 1;
    puVar2[0x30] = 1;
    puVar2[0x41] = 2;
    puVar2[0x42] = 2;
    puVar2[0x3f] = 4;
    puVar2[0x43] = 0;
    puVar2[0x44] = 0;
    puVar2[0x45] = 0;
    return;
  default:
    puVar2 = *(undefined4 **)param_1;
    puVar2[5] = 9;
    (*(code *)*puVar2)(param_1);
    return;
  }
  *(undefined4 *)((int)param_1 + 0x40) = 1;
  *(undefined4 *)((int)param_1 + 0xdc) = 0;
  *(undefined4 *)((int)param_1 + 0xe0) = 1;
  *(undefined4 *)((int)param_1 + 0xe4) = 1;
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
}
