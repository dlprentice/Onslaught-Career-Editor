/* address: 0x0058070e */
/* name: CFastVB__InitDualTexelConversionPipeline */
/* signature: int __thiscall CFastVB__InitDualTexelConversionPipeline(void * this, void * param_1, int param_2, int param_3, uint param_4) */


int __thiscall
CFastVB__InitDualTexelConversionPipeline
          (void *this,void *param_1,int param_2,int param_3,uint param_4)

{
  int *piVar1;
  int iVar2;
  int unaff_EDI;

  *(undefined4 *)((int)this + 4) = 0;
  *(undefined4 *)this = 0;
  *(int *)((int)this + 8) = param_3;
  if ((((param_3 & 0xffffU) == 0) || (5 < (param_3 & 0xffffU))) || ((param_3 & 0xffc00000U) != 0)) {
    return -0x7789f794;
  }
  *(uint *)(param_2 + 0x44) = param_3 & 0x100000;
  *(uint *)((int)param_1 + 0x44) = param_3 & 0x200000;
  *(uint *)((int)param_1 + 0x40) = param_3 & 0x80000;
  piVar1 = CFastVB__CreateTexelUnpackProfileByFormat(param_1);
  *(int **)((int)this + 4) = piVar1;
  if (piVar1 != (int *)0x0) {
    piVar1 = CFastVB__CreateTexelUnpackProfileByFormat((void *)param_2);
    *(int **)this = piVar1;
    if (piVar1 != (int *)0x0) {
      iVar2 = CFastVB__Helper_00581cc0(*(void **)((int)this + 4),(int)piVar1,unaff_EDI);
      if (iVar2 < 0) goto LAB_0058080f;
      iVar2 = CFastVB__Helper_0057e0c3(this);
      if ((((-1 < iVar2) || (iVar2 = CFastVB__BlendEqualDimensionVolumeData(this), -1 < iVar2)) ||
          ((iVar2 = CFastVB__BlendClampedVolumeData(this), -1 < iVar2 ||
           ((iVar2 = CFastVB__Helper_0057e4d3(this), -1 < iVar2 ||
            (iVar2 = CFastVB__Helper_0057e6cc(this), -1 < iVar2)))))) ||
         ((iVar2 = CFastVB__Helper_0057eadb(this), -1 < iVar2 ||
          ((((iVar2 = CFastVB__Helper_0057f002(this), -1 < iVar2 ||
             (iVar2 = CFastVB__Helper_0057f391(this), -1 < iVar2)) ||
            (iVar2 = CFastVB__RunDualProfileConversionStage(this), -1 < iVar2)) ||
           (iVar2 = CFastVB__Unk_0057fa5c(this), -1 < iVar2)))))) {
        iVar2 = 0;
        goto LAB_0058080f;
      }
    }
  }
  iVar2 = -0x7fffbffb;
LAB_0058080f:
  if (*(undefined4 **)((int)this + 4) != (undefined4 *)0x0) {
    (**(code **)**(undefined4 **)((int)this + 4))(1);
    *(undefined4 *)((int)this + 4) = 0;
  }
  if (*(undefined4 **)this != (undefined4 *)0x0) {
    (**(code **)**(undefined4 **)this)(1);
    *(undefined4 *)this = 0;
  }
  return iVar2;
}
