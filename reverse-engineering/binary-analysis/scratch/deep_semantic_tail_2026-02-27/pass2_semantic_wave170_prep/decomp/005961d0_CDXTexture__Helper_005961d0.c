/* address: 0x005961d0 */
/* name: CDXTexture__Helper_005961d0 */
/* signature: void __stdcall CDXTexture__Helper_005961d0(void * param_1, void * param_2, void * param_3) */


void CDXTexture__Helper_005961d0(void *param_1,void *param_2,void *param_3)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  int iVar5;
  int iVar6;
  undefined4 *puVar7;
  float10 fVar8;
  float10 fVar9;
  float10 fVar10;
  float10 fVar11;
  undefined4 local_44 [16];

  if (param_3 == param_1) {
    if (param_2 != param_1) {
      iVar6 = -4;
      do {
        iVar5 = -0x10;
        fVar8 = (float10)*(float *)((int)param_3 + iVar6 * 4 + 0x10);
        fVar9 = (float10)*(float *)((int)param_3 + iVar6 * 4 + 0x20);
        fVar10 = (float10)*(float *)((int)param_3 + iVar6 * 4 + 0x30);
        fVar11 = (float10)*(float *)((int)param_3 + iVar6 * 4 + 0x40);
        do {
          *(float *)((int)param_1 + iVar5 * 4 + 0x40) =
               (float)(fVar11 * (float10)*(float *)((int)param_2 + iVar5 * 4 + 0x4c) +
                       fVar9 * (float10)*(float *)((int)param_2 + iVar5 * 4 + 0x44) +
                      fVar8 * (float10)*(float *)((int)param_2 + iVar5 * 4 + 0x40) +
                      fVar10 * (float10)*(float *)((int)param_2 + iVar5 * 4 + 0x48));
          iVar5 = iVar5 + 4;
        } while (iVar5 != 0);
        ffree(fVar8);
        ffree(fVar9);
        ffree(fVar10);
        ffree(fVar11);
        param_1 = (void *)((int)param_1 + 4);
        iVar6 = iVar6 + 1;
      } while (iVar6 != 0);
      return;
    }
    puVar7 = local_44;
    for (iVar6 = 0x10; iVar6 != 0; iVar6 = iVar6 + -1) {
      *puVar7 = *(undefined4 *)param_3;
      param_3 = (undefined4 *)((int)param_3 + 4);
      puVar7 = puVar7 + 1;
    }
    param_3 = local_44;
  }
  iVar6 = -4;
  do {
    iVar5 = -4;
    fVar1 = *(float *)param_2;
    fVar2 = *(float *)((int)param_2 + 4);
    fVar3 = *(float *)((int)param_2 + 8);
    fVar4 = *(float *)((int)param_2 + 0xc);
    do {
      *(float *)((int)param_1 + iVar5 * 4 + 0x10) =
           (float)((float10)fVar4 * (float10)*(float *)((int)param_3 + iVar5 * 4 + 0x40) +
                   (float10)fVar2 * (float10)*(float *)((int)param_3 + iVar5 * 4 + 0x20) +
                  (float10)fVar1 * (float10)*(float *)((int)param_3 + iVar5 * 4 + 0x10) +
                  (float10)fVar3 * (float10)*(float *)((int)param_3 + iVar5 * 4 + 0x30));
      iVar5 = iVar5 + 1;
    } while (iVar5 != 0);
    ffree((float10)fVar1);
    ffree((float10)fVar2);
    ffree((float10)fVar3);
    ffree((float10)fVar4);
    param_2 = (void *)((int)param_2 + 0x10);
    param_1 = (void *)((int)param_1 + 0x10);
    iVar6 = iVar6 + 1;
  } while (iVar6 != 0);
  return;
}
