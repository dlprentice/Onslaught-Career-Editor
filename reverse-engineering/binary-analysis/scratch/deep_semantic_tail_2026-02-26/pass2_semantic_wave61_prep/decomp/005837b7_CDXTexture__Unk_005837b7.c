/* address: 0x005837b7 */
/* name: CDXTexture__Unk_005837b7 */
/* signature: void __thiscall CDXTexture__Unk_005837b7(void * this, void * param_1, uint param_2, float param_3, uint param_4) */


void __thiscall
CDXTexture__Unk_005837b7(void *this,void *param_1,uint param_2,float param_3,uint param_4)

{
  float fVar1;
  undefined1 *puVar2;
  float *pfVar3;
  float fVar4;
  int unaff_ESI;
  float *pfVar5;

  if (*(int *)((int)this + 0x1050) != 0) {
    param_3 = (float)CFastVB__Helper_00581279(this,(int)param_3,unaff_ESI);
  }
  if (*(int *)((int)this + 0x10) != 0) {
    param_3 = (float)CDXTexture__Helper_00581e8c(this,(int)param_3,unaff_ESI);
  }
  puVar2 = (undefined1 *)
           (*(int *)((int)this + 0x1058) * (int)param_1 + *(int *)((int)this + 0x105c) * param_2 +
           *(int *)((int)this + 0x20));
  param_1 = (void *)0x0;
  if (*(int *)((int)this + 0x1060) != 0) {
    pfVar3 = (float *)((int)param_3 + 8);
    do {
      fVar4 = 0.0;
      param_2 = 0x7f7fffff;
      param_3 = 0.0;
      pfVar5 = (float *)((int)this + 0x40);
      do {
        fVar1 = (pfVar3[-2] - pfVar5[-2]) * (pfVar3[-2] - pfVar5[-2]) +
                (pfVar3[-1] - pfVar5[-1]) * (pfVar3[-1] - pfVar5[-1]) +
                (*pfVar3 - *pfVar5) * (*pfVar3 - *pfVar5) +
                (pfVar3[1] - pfVar5[1]) * (pfVar3[1] - pfVar5[1]);
        if (fVar1 < (float)param_2) {
          fVar4 = param_3;
          param_2 = (uint)fVar1;
        }
        param_3 = (float)((int)param_3 + 1);
        pfVar5 = pfVar5 + 4;
      } while ((uint)param_3 < 0x100);
      *puVar2 = SUB41(fVar4,0);
      puVar2 = puVar2 + 1;
      param_1 = (void *)((int)param_1 + 1);
      pfVar3 = pfVar3 + 4;
    } while (param_1 < *(void **)((int)this + 0x1060));
  }
  return;
}
