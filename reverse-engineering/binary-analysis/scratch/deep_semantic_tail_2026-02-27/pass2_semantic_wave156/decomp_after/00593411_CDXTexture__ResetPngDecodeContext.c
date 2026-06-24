/* address: 0x00593411 */
/* name: CDXTexture__ResetPngDecodeContext */
/* signature: void __stdcall CDXTexture__ResetPngDecodeContext(void * param_1, int param_2, int param_3) */


void CDXTexture__ResetPngDecodeContext(void *param_1,int param_2,int param_3)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  int iVar4;
  undefined4 *puVar5;
  int iVar6;
  undefined4 *puVar7;
  undefined4 local_44 [16];

  iVar6 = 0;
  if (param_2 != 0) {
    CDXTexture__ZeroDecodeWorkspace16Dwords((int)param_1,(void *)param_2);
  }
  if (param_3 != 0) {
    CDXTexture__ZeroDecodeWorkspace16Dwords((int)param_1,(void *)param_3);
  }
  CDXTexture__Helper_0059ccb3((int)param_1,*(int *)((int)param_1 + 0x9c));
  CDXTexture__Helper_0059ccb3((int)param_1,*(int *)((int)param_1 + 0xdc));
  CDXTexture__Helper_0059ccb3((int)param_1,*(int *)((int)param_1 + 0xd8));
  CDXTexture__Helper_0059ccb3((int)param_1,*(int *)((int)param_1 + 0x174));
  CDXTexture__Helper_0059ccb3((int)param_1,*(int *)((int)param_1 + 0x178));
  CDXTexture__Helper_0059ccb3((int)param_1,*(int *)((int)param_1 + 0x138));
  if ((*(byte *)((int)param_1 + 0x5d) & 0x10) != 0) {
    CDXTexture__FreeDecodeBufferIfPresent((int)param_1,*(int *)((int)param_1 + 0x104));
  }
  if ((*(byte *)((int)param_1 + 0x5d) & 0x20) != 0) {
    CDXTexture__Helper_0059ccb3((int)param_1,*(int *)((int)param_1 + 0x15c));
  }
  if (*(int *)((int)param_1 + 0x144) != 0) {
    iVar4 = 1 << (8U - (char)*(undefined4 *)((int)param_1 + 300) & 0x1f);
    if (0 < iVar4) {
      do {
        CDXTexture__Helper_0059ccb3
                  ((int)param_1,*(int *)(*(int *)((int)param_1 + 0x144) + iVar6 * 4));
        iVar6 = iVar6 + 1;
      } while (iVar6 < iVar4);
    }
    CDXTexture__Helper_0059ccb3((int)param_1,*(int *)((int)param_1 + 0x144));
  }
  CDXTexture__Unk_0059c78f((int)param_1 + 100);
  uVar1 = *(undefined4 *)((int)param_1 + 0x48);
  uVar2 = *(undefined4 *)((int)param_1 + 0x40);
  puVar5 = param_1;
  puVar7 = local_44;
  for (iVar6 = 0x10; iVar6 != 0; iVar6 = iVar6 + -1) {
    *puVar7 = *puVar5;
    puVar5 = puVar5 + 1;
    puVar7 = puVar7 + 1;
  }
  uVar3 = *(undefined4 *)((int)param_1 + 0x44);
  puVar5 = param_1;
  for (iVar6 = 0x67; iVar6 != 0; iVar6 = iVar6 + -1) {
    *puVar5 = 0;
    puVar5 = puVar5 + 1;
  }
  *(undefined4 *)((int)param_1 + 0x44) = uVar3;
  puVar5 = local_44;
  puVar7 = param_1;
  for (iVar6 = 0x10; iVar6 != 0; iVar6 = iVar6 + -1) {
    *puVar7 = *puVar5;
    puVar5 = puVar5 + 1;
    puVar7 = puVar7 + 1;
  }
  *(undefined4 *)((int)param_1 + 0x40) = uVar2;
  *(undefined4 *)((int)param_1 + 0x48) = uVar1;
  return;
}
