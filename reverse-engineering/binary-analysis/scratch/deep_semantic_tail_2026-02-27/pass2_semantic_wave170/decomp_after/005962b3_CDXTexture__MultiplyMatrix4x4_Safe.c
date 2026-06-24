/* address: 0x005962b3 */
/* name: CDXTexture__MultiplyMatrix4x4_Safe */
/* signature: void __stdcall CDXTexture__MultiplyMatrix4x4_Safe(void * param_1, void * param_2, void * param_3) */


void CDXTexture__MultiplyMatrix4x4_Safe(void *param_1,void *param_2,void *param_3)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  undefined4 *puVar5;
  float *pfVar6;
  int iVar7;
  int iVar8;
  undefined4 local_48 [17];

  if ((param_1 == param_2) || (puVar5 = param_1, param_1 == param_3)) {
    puVar5 = local_48;
  }
  iVar8 = -4;
  do {
    iVar7 = -4;
    pfVar6 = (float *)(puVar5 + iVar8 + 4);
    fVar1 = *(float *)param_2;
    fVar2 = *(float *)((int)param_2 + 4);
    fVar3 = *(float *)((int)param_2 + 8);
    fVar4 = *(float *)((int)param_2 + 0xc);
    do {
      *pfVar6 = (float)((float10)fVar4 * (float10)*(float *)((int)param_3 + iVar7 * 4 + 0x40) +
                        (float10)fVar2 * (float10)*(float *)((int)param_3 + iVar7 * 4 + 0x20) +
                       (float10)fVar1 * (float10)*(float *)((int)param_3 + iVar7 * 4 + 0x10) +
                       (float10)fVar3 * (float10)*(float *)((int)param_3 + iVar7 * 4 + 0x30));
      pfVar6 = pfVar6 + 4;
      iVar7 = iVar7 + 1;
    } while (iVar7 != 0);
    ffree((float10)fVar1);
    ffree((float10)fVar2);
    ffree((float10)fVar3);
    ffree((float10)fVar4);
    param_2 = (void *)((int)param_2 + 0x10);
    iVar8 = iVar8 + 1;
  } while (iVar8 != 0);
  if (puVar5 != param_1) {
    for (iVar8 = 0x10; iVar8 != 0; iVar8 = iVar8 + -1) {
      *(undefined4 *)param_1 = *puVar5;
      puVar5 = puVar5 + 1;
      param_1 = (undefined4 *)((int)param_1 + 4);
    }
  }
  return;
}
