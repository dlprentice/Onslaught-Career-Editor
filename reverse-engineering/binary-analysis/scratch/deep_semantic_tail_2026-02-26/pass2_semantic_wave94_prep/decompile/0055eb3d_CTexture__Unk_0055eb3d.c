/* address: 0x0055eb3d */
/* name: CTexture__Unk_0055eb3d */
/* signature: double __cdecl CTexture__Unk_0055eb3d(double param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

double __cdecl CTexture__Unk_0055eb3d(double param_1)

{
  uint uVar1;
  int iVar2;
  int unaff_ESI;
  float10 fVar3;
  float10 extraout_ST0;
  double dVar4;
  uint uVar5;

  uVar1 = CTexture__Helper_00562c76();
  uVar5 = (uint)((ulonglong)param_1 >> 0x20);
  if ((param_1._6_2_ & 0x7ff0) == 0x7ff0) {
    iVar2 = CFastVB__Unk_00562b3e(SUB84(param_1,0),uVar5);
    if (0 < iVar2) {
      if (iVar2 < 3) {
        CTexture__Helper_00562c76();
        fVar3 = (float10)param_1;
        goto LAB_0055ec08;
      }
      if (iVar2 == 3) {
        dVar4 = CTexture__Helper_0056244b(0xc,(double)CONCAT44(uVar1,uVar5),unaff_ESI);
        fVar3 = (float10)dVar4;
        goto LAB_0055ec08;
      }
    }
  }
  else {
    fVar3 = (float10)__frnd();
    if (((double)fVar3 == param_1) || ((uVar1 & 0x20) != 0)) {
      CTexture__Helper_00562c76();
      fVar3 = (float10)(double)fVar3;
      goto LAB_0055ec08;
    }
  }
  CTexture__Helper_0056249f();
  fVar3 = extraout_ST0;
LAB_0055ec08:
  return (double)fVar3;
}
