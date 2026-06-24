/* address: 0x0056e8aa */
/* name: CDXTexture__Helper_0056e8aa */
/* signature: int __cdecl CDXTexture__Helper_0056e8aa(void * param_1, int param_2) */


int __cdecl CDXTexture__Helper_0056e8aa(void *param_1,int param_2)

{
  char *pcVar1;
  int iVar2;

  iVar2 = param_2;
  for (pcVar1 = param_1; (iVar2 != 0 && (iVar2 = iVar2 + -1, *pcVar1 != '\0')); pcVar1 = pcVar1 + 1)
  {
  }
  if (*pcVar1 != '\0') {
    return param_2;
  }
  return (int)pcVar1 - (int)param_1;
}
