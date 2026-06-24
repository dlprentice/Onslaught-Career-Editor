/* address: 0x005ab14b */
/* name: CTexture__SerializeNodeTreeToBitstream */
/* signature: int __stdcall CTexture__SerializeNodeTreeToBitstream(int param_1, int param_2, uint param_3, int param_4) */


int CTexture__SerializeNodeTreeToBitstream(int param_1,int param_2,uint param_3,int param_4)

{
  int iVar1;
  void *ptr;
  int iVar2;
  void *pvVar3;
  ushort local_a;

  if (param_4 == 0) {
    iVar1 = 0;
  }
  else {
    for (; iVar1 = *(int *)(param_2 + 4), iVar1 != 1; param_2 = *(int *)(param_2 + 0x10)) {
      if (iVar1 != 7) {
        if (iVar1 != 8) {
          return -0x7fffbffb;
        }
        switch(*(undefined4 *)(param_2 + 0x14)) {
        case 0:
          break;
        case 1:
        case 2:
        case 3:
        case 4:
        case 5:
        case 6:
        case 7:
        case 8:
        case 0xd:
          break;
        case 9:
        case 10:
        case 0xb:
        case 0xc:
          break;
        case 0xe:
          break;
        case 0xf:
          break;
        case 0x10:
          break;
        case 0x11:
          break;
        case 0x12:
          break;
        case 0x13:
          break;
        case 0x14:
          break;
        case 0x15:
          break;
        case 0x16:
          break;
        case 0x17:
          break;
        case 0x18:
          break;
        case 0x19:
          break;
        case 0x1a:
          break;
        case 0x1b:
          break;
        case 0x1c:
        }
        iVar1 = CDXTexture__Helper_0059902a();
        goto LAB_005ab39e;
      }
    }
    CDXTexture__EvalNodeOutputSizeUnits(param_2);
    local_a = 0;
    iVar1 = param_2;
    do {
      local_a = local_a + 1;
      iVar1 = *(int *)(iVar1 + 0xc);
    } while (iVar1 != 0);
    CFastVB__Helper_00426fd0((uint)local_a << 3);
    pvVar3 = ptr;
    if (ptr == (void *)0x0) {
      iVar1 = -0x7ff8fff2;
    }
    else {
      do {
        iVar1 = *(int *)(*(int *)(param_2 + 8) + 0x18);
        iVar2 = CDXTexture__Helper_0059902a();
        if (iVar2 < 0) {
          OID__FreeObject_Callback(ptr);
          return iVar2;
        }
        iVar1 = CTexture__SerializeNodeTreeToBitstream
                          (param_1,*(int *)(iVar1 + 0x20),1,(int)pvVar3 + 4);
        if (iVar1 < 0) {
          OID__FreeObject_Callback(ptr);
          return iVar1;
        }
        param_2 = *(int *)(param_2 + 0xc);
        pvVar3 = (void *)((int)pvVar3 + 8);
      } while (param_2 != 0);
      iVar1 = CDXTexture__Helper_0059902a();
      OID__FreeObject_Callback(ptr);
      if (-1 < iVar1) {
        iVar1 = CDXTexture__Helper_0059902a();
LAB_005ab39e:
        if (-1 < iVar1) {
          iVar1 = 0;
        }
      }
    }
  }
  return iVar1;
}
