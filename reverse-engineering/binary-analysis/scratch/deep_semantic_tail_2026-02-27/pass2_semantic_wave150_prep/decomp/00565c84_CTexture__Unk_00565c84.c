/* address: 0x00565c84 */
/* name: CTexture__Unk_00565c84 */
/* signature: int __cdecl CTexture__Unk_00565c84(void * param_1, void * param_2, void * param_3, void * param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __cdecl CTexture__Unk_00565c84(void *param_1,void *param_2,void *param_3,void *param_4)

{
  int iVar1;
  undefined *puVar2;
  undefined1 local_8c [136];

  if (param_1 == (void *)0x0) {
LAB_00565d2a:
    puVar2 = (undefined *)0x0;
  }
  else {
    if ((*(char *)param_1 == 'C') && (*(char *)((int)param_1 + 1) == '\0')) {
      *(undefined1 *)((int)param_2 + 1) = 0;
      *(undefined1 *)param_2 = 0x43;
      if (param_3 != (void *)0x0) {
        *(undefined2 *)param_3 = 0;
        *(undefined2 *)((int)param_3 + 2) = 0;
        *(undefined2 *)((int)param_3 + 4) = 0;
      }
      if (param_4 == (void *)0x0) {
        return (int)param_2;
      }
      *(undefined4 *)param_4 = 0;
      return (int)param_2;
    }
    iVar1 = _strcmp(&DAT_00653ca8,param_1);
    if ((iVar1 != 0) && (iVar1 = _strcmp(&DAT_00653c24,param_1), iVar1 != 0)) {
      iVar1 = CTexture__Helper_00565dc1(local_8c,param_1);
      if ((iVar1 != 0) ||
         (iVar1 = CTexture__Helper_0056c0da(local_8c,&DAT_009d0984,(int)local_8c), iVar1 == 0))
      goto LAB_00565d2a;
      _DAT_009d098c = (uint)DAT_009d0988;
      CTexture__Helper_00565e8d(0x653ca8,(int)local_8c);
      if (*(char *)param_1 == '\0') {
        param_1 = &DAT_00653ca8;
      }
      CDXTexture__Helper_00567de0(&DAT_00653c24,param_1);
    }
    if (param_3 != (void *)0x0) {
      CTexture__Helper_00567700(param_3,&DAT_009d0984,6);
    }
    if (param_4 != (void *)0x0) {
      CTexture__Helper_00567700(param_4,&DAT_009d098c,4);
    }
    CDXTexture__Helper_00567de0(param_2,&DAT_00653ca8);
    puVar2 = &DAT_00653ca8;
  }
  return (int)puVar2;
}
