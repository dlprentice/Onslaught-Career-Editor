/* address: 0x00596106 */
/* name: CDXTexture__Helper_00596106 */
/* signature: float * __stdcall CDXTexture__Helper_00596106(void * param_1, void * param_2) */


float * CDXTexture__Helper_00596106(void *param_1,void *param_2)

{
  float fVar1;
  float fVar2;
  float fVar3;
  uint uVar4;
  float10 fVar5;

  fVar5 = (float10)*(float *)param_2 * (float10)*(float *)param_2 +
          (float10)*(float *)((int)param_2 + 4) * (float10)*(float *)((int)param_2 + 4) +
          (float10)*(float *)((int)param_2 + 8) * (float10)*(float *)((int)param_2 + 8);
  fVar1 = (float)fVar5;
  if (fVar1 == 0.0) {
    ffree(fVar5);
    *(undefined4 *)param_1 = 0;
    *(undefined4 *)((int)param_1 + 4) = 0;
    *(undefined4 *)((int)param_1 + 8) = 0;
  }
  else if ((uint)ABS((float)(fVar5 - (float10)1)) < 0x3727c5ad) {
    if (param_1 != param_2) {
      *(undefined4 *)param_1 = *(undefined4 *)param_2;
      *(undefined4 *)((int)param_1 + 4) = *(undefined4 *)((int)param_2 + 4);
      *(undefined4 *)((int)param_1 + 8) = *(undefined4 *)((int)param_2 + 8);
    }
  }
  else {
    uVar4 = (uint)fVar1 >> 0xc & 0xff8;
    fVar3 = ((float)((uint)fVar1 & 0xffffff | 0x3f000000) * *(float *)(&DAT_00658c98 + uVar4) +
            *(float *)(&DAT_00658c9c + uVar4)) * (float)(0xbeffffffU - (int)fVar1 >> 1 & 0xff800000)
    ;
    fVar1 = *(float *)((int)param_2 + 4);
    fVar2 = *(float *)((int)param_2 + 8);
    *(float *)param_1 = *(float *)param_2 * fVar3;
    *(float *)((int)param_1 + 4) = fVar1 * fVar3;
    *(float *)((int)param_1 + 8) = fVar2 * fVar3;
  }
  return param_1;
}
