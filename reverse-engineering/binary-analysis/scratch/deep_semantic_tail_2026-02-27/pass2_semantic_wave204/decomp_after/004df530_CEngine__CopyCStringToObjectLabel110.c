/* address: 0x004df530 */
/* name: CEngine__CopyCStringToObjectLabel110 */
/* signature: void __thiscall CEngine__CopyCStringToObjectLabel110(void * this, int param_1, void * param_2) */


void __thiscall CEngine__CopyCStringToObjectLabel110(void *this,int param_1,void *param_2)

{
  char cVar1;
  char *pcVar2;

  cVar1 = *(char *)param_1;
  if (cVar1 != '\0') {
    pcVar2 = (char *)((int)this + 0x110);
    do {
      *pcVar2 = cVar1;
      cVar1 = *(char *)(param_1 + 1);
      pcVar2 = pcVar2 + 1;
      param_1 = param_1 + 1;
    } while (cVar1 != '\0');
  }
  return;
}
