/* address: 0x00581e1c */
/* name: CFastVB__TexelUnpackProfile__ZeroTexelsMatchingKeyColor */
/* signature: void __thiscall CFastVB__TexelUnpackProfile__ZeroTexelsMatchingKeyColor(void * this, int param_1, uint param_2) */


void __thiscall
CFastVB__TexelUnpackProfile__ZeroTexelsMatchingKeyColor(void *this,int param_1,uint param_2)

{
  uint uVar1;
  int iVar2;
  float *pfVar3;

  uVar1 = *(int *)((int)this + 0x1060) * 0x10 + param_1;
  if ((uint)param_1 < uVar1) {
    iVar2 = ((uVar1 - param_1) - 1 >> 4) + 1;
    pfVar3 = (float *)(param_1 + 8);
    do {
      if ((((pfVar3[-2] == *(float *)((int)this + 0x24)) &&
           (pfVar3[-1] == *(float *)((int)this + 0x28))) &&
          (*pfVar3 == *(float *)((int)this + 0x2c))) && (pfVar3[1] == *(float *)((int)this + 0x30)))
      {
        pfVar3[1] = 0.0;
        *pfVar3 = 0.0;
        pfVar3[-1] = 0.0;
        pfVar3[-2] = 0.0;
      }
      pfVar3 = pfVar3 + 4;
      iVar2 = iVar2 + -1;
    } while (iVar2 != 0);
  }
  return;
}
