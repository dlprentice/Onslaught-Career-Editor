/* address: 0x00568667 */
/* name: CRT__PowSpecialCaseCore */
/* signature: int __cdecl CRT__PowSpecialCaseCore(int param_1, int param_2, double param_3, void * param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __cdecl CRT__PowSpecialCaseCore(int param_1,int param_2,double param_3,void *param_4)

{
  double dVar1;
  double dVar2;
  int iVar3;
  undefined4 unaff_ESI;

  dVar1 = (double)CONCAT44(param_2,param_1);
  if ((double)CONCAT44(param_2,param_1) < _DAT_005d87b0) {
    dVar1 = -dVar1;
  }
  dVar2 = _DAT_00653840;
  if (param_3._4_4_ == 0x7ff00000) {
    if (param_3._0_4_ != 0) {
LAB_005686f2:
      if (param_2 == 0x7ff00000) {
        if (param_1 != 0) {
          return 0;
        }
        if (_DAT_005d87b0 < param_3) goto LAB_0056878d;
        if (param_3 < _DAT_005d87b0) goto LAB_00568724;
      }
      else {
        if (param_2 != -0x100000) {
          return 0;
        }
        if (param_1 != 0) {
          return 0;
        }
        iVar3 = CRT__PowClassifyIntegralExponent
                          ((void *)0xfff00000,param_3._0_4_,
                           (double)CONCAT44(SUB84(dVar1,0),unaff_ESI));
        if (_DAT_005d87b0 < param_3) {
          dVar2 = _DAT_00653840;
          if (iVar3 == 1) {
            dVar2 = -_DAT_00653840;
          }
          goto LAB_0056878d;
        }
        if (param_3 < _DAT_005d87b0) {
          dVar2 = _DAT_00653860;
          if (iVar3 != 1) {
            dVar2 = 0.0;
          }
          goto LAB_0056878d;
        }
      }
      dVar2 = 1.0;
      goto LAB_0056878d;
    }
    if (_DAT_005d87e0 < dVar1) goto LAB_0056878d;
    if (_DAT_005d87e0 <= dVar1) {
LAB_005686b7:
      *(undefined8 *)param_4 = _DAT_00653848;
      return 1;
    }
  }
  else {
    if (param_3 != -INFINITY) goto LAB_005686f2;
    if (dVar1 <= _DAT_005d87e0) {
      if (_DAT_005d87e0 <= dVar1) goto LAB_005686b7;
      goto LAB_0056878d;
    }
  }
LAB_00568724:
  dVar2 = 0.0;
LAB_0056878d:
  *(double *)param_4 = dVar2;
  return 0;
}
