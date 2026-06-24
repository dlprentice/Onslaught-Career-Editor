/* address: 0x0056c257 */
/* name: CTexture__Helper_0056c257 */
/* signature: void __cdecl CTexture__Helper_0056c257(int param_1, int param_2, void * param_3) */


void __cdecl CTexture__Helper_0056c257(int param_1,int param_2,void *param_3)

{
  int iVar1;
  int iVar2;
  int iVar3;

  iVar2 = 0;
  iVar1 = 1;
  if (-1 < param_2) {
    do {
      if (iVar1 == 0) {
        return;
      }
      iVar3 = (param_2 + iVar2) / 2;
      iVar1 = stricmp(*(char **)param_3,*(char **)(param_1 + iVar3 * 8));
      if (iVar1 == 0) {
        *(int *)param_3 = param_1 + iVar3 * 8 + 4;
      }
      else if (iVar1 < 0) {
        param_2 = iVar3 + -1;
      }
      else {
        iVar2 = iVar3 + 1;
      }
    } while (iVar2 <= param_2);
  }
  return;
}
