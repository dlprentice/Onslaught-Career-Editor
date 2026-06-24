/* address: 0x0055f44b */
/* name: CTokenArchive__Helper_0055f44b */
/* signature: uint __cdecl CTokenArchive__Helper_0055f44b(int param_1, uint param_2, uint param_3, int param_4, void * param_5) */


uint __cdecl
CTokenArchive__Helper_0055f44b(int param_1,uint param_2,uint param_3,int param_4,void *param_5)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;

  uVar4 = (param_3 - 1) * param_4 + param_2;
  if (param_2 <= uVar4) {
    do {
      uVar3 = param_3 >> 1;
      if (uVar3 == 0) {
        if (param_3 == 0) {
          return 0;
        }
        iVar2 = (*param_5)(param_1,param_2);
        return ~-(uint)(iVar2 != 0) & param_2;
      }
      uVar1 = uVar3;
      if ((param_3 & 1) == 0) {
        uVar1 = uVar3 - 1;
      }
      uVar1 = uVar1 * param_4 + param_2;
      iVar2 = (*param_5)(param_1,uVar1);
      if (iVar2 == 0) {
        return uVar1;
      }
      if (iVar2 < 0) {
        uVar4 = uVar1 - param_4;
        if ((param_3 & 1) == 0) {
          uVar3 = uVar3 - 1;
        }
      }
      else {
        param_2 = uVar1 + param_4;
      }
      param_3 = uVar3;
    } while (param_2 <= uVar4);
  }
  return 0;
}
