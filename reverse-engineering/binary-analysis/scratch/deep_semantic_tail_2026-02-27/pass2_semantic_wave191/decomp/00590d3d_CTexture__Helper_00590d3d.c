/* address: 0x00590d3d */
/* name: CTexture__Helper_00590d3d */
/* signature: int __stdcall CTexture__Helper_00590d3d(int param_1, void * param_2) */


int CTexture__Helper_00590d3d(int param_1,void *param_2)

{
  int iVar1;
  void *extraout_EAX;
  int *extraout_EAX_00;
  int *piVar2;

  if (param_2 == (void *)0x0) {
    iVar1 = -0x7789f794;
  }
  else {
    OID__AllocObject_DefaultTag_00662b2c(0x10);
    if (extraout_EAX == (void *)0x0) {
      piVar2 = (int *)0x0;
    }
    else {
      CTexture__Helper_00590d25(extraout_EAX);
      piVar2 = extraout_EAX_00;
    }
    if (piVar2 == (int *)0x0) {
      iVar1 = -0x7ff8fff2;
    }
    else {
      iVar1 = (**(code **)(*piVar2 + 0x18))(param_1);
      if (iVar1 < 0) {
        (**(code **)(*piVar2 + 0x14))(1);
      }
      else {
        *(int **)param_2 = piVar2;
        iVar1 = 0;
      }
    }
  }
  return iVar1;
}
