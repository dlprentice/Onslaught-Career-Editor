/* address: 0x005605ca */
/* name: CDXTexture__Helper_005605ca */
/* signature: int __cdecl CDXTexture__Helper_005605ca(void * param_1, void * param_2, void * param_3) */


int __cdecl CDXTexture__Helper_005605ca(void *param_1,void *param_2,void *param_3)

{
  int iVar1;

  iVar1 = *(int *)((int)param_1 + 4);
  if ((iVar1 == 0) || (*(char *)(iVar1 + 8) == '\0')) {
LAB_00560621:
    iVar1 = 1;
  }
  else {
    if (iVar1 == *(int *)((int)param_2 + 4)) {
LAB_005605fb:
      if (((((*(byte *)param_2 & 2) == 0) || ((*(byte *)param_1 & 8) != 0)) &&
          (((*(uint *)param_3 & 1) == 0 || ((*(byte *)param_1 & 1) != 0)))) &&
         (((*(uint *)param_3 & 2) == 0 || ((*(byte *)param_1 & 2) != 0)))) goto LAB_00560621;
    }
    else {
      iVar1 = _strcmp((char *)(iVar1 + 8),(char *)(*(int *)((int)param_2 + 4) + 8));
      if (iVar1 == 0) goto LAB_005605fb;
    }
    iVar1 = 0;
  }
  return iVar1;
}
