/* address: 0x0040ac50 */
/* name: CGeneralVolume__Unk_0040ac50 */
/* signature: void __thiscall CGeneralVolume__Unk_0040ac50(void * this, int param_1, float param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall CGeneralVolume__Unk_0040ac50(void *this,int param_1,float param_2)

{
  float fVar1;
  float *pfVar2;
  int iVar3;
  float *pfVar4;

  if (_DAT_005d856c < (float)param_1) {
    pfVar2 = (float *)((int)this + 0x52c);
    iVar3 = 6;
    do {
      if (pfVar2[0xc] == 0.0) {
        fVar1 = (float)param_1 *
                *(float *)((int)pfVar2 + *(int *)((int)this + 0x4b0) + (-0x4a4 - (int)this)) +
                *pfVar2;
        *pfVar2 = fVar1;
        pfVar4 = (float *)((int)pfVar2 + *(int *)((int)this + 0x4b0) + (-0x4a4 - (int)this));
        if (*pfVar4 < fVar1) {
          *pfVar2 = *pfVar4;
        }
      }
      pfVar2 = pfVar2 + 1;
      iVar3 = iVar3 + -1;
    } while (iVar3 != 0);
  }
  return;
}
