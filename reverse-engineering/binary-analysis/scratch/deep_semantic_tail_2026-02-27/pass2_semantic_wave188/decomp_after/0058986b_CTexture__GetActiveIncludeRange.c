/* address: 0x0058986b */
/* name: CTexture__GetActiveIncludeRange */
/* signature: int __thiscall CTexture__GetActiveIncludeRange(void * this, int param_1, void * param_2, void * param_3) */


int __thiscall CTexture__GetActiveIncludeRange(void *this,int param_1,void *param_2,void *param_3)

{
  uint *puVar1;
  uint *puVar2;

  puVar1 = *(uint **)((int)this + 0x50);
  do {
    puVar2 = puVar1;
    puVar1 = (uint *)puVar2[0x1b];
  } while ((uint *)puVar2[0x1b] != (uint *)0x0);
  if (param_1 != 0) {
    *(uint *)param_1 = *puVar2;
  }
  if (param_2 != (void *)0x0) {
    if (puVar2[1] < *puVar2) {
      *(undefined4 *)param_2 = 0;
    }
    else {
      *(uint *)param_2 = puVar2[1] - *puVar2;
    }
  }
  return 0;
}
