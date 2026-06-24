/* address: 0x0058e309 */
/* name: CTexture__Helper_0058e309 */
/* signature: uint __thiscall CTexture__Helper_0058e309(void * this, void * param_1, int param_2) */


uint __thiscall CTexture__Helper_0058e309(void *this,void *param_1,int param_2)

{
  uint uVar1;
  char cVar2;
  char *pcVar3;
  int iStack_1c;
  uint local_c;
  uint local_8;

  pcVar3 = *(char **)((int)param_1 + 8);
  iStack_1c = 0;
  local_c = 0;
  if ((pcVar3 == (char *)0x0) || (*pcVar3 == '\0')) {
    local_c = 0xe40000;
  }
  else {
    local_8 = 0x10;
    do {
      cVar2 = *pcVar3;
      if (cVar2 != '\0') {
        if (cVar2 < 'x') {
          if ((cVar2 == 'w') || (cVar2 == 'a')) {
            iStack_1c = 3;
          }
          else {
            if (cVar2 != 'b') {
              if (cVar2 == 'g') goto LAB_0058e3ad;
              if (cVar2 == 'r') goto LAB_0058e35a;
              goto LAB_0058e376;
            }
LAB_0058e3a9:
            iStack_1c = 2;
          }
        }
        else if (cVar2 == 'x') {
LAB_0058e35a:
          iStack_1c = 0;
        }
        else {
          if (cVar2 != 'y') {
            if (cVar2 == 'z') goto LAB_0058e3a9;
            goto LAB_0058e376;
          }
LAB_0058e3ad:
          iStack_1c = 1;
        }
        pcVar3 = pcVar3 + 1;
      }
      uVar1 = local_8 + 2;
      local_c = local_c | iStack_1c << ((byte)local_8 & 0x1f);
      local_8 = uVar1;
    } while (uVar1 < 0x18);
    if (*pcVar3 != '\0') {
LAB_0058e376:
      CTexture__Helper_0058c893(*(void **)this,(int)param_1,0x7d4,0x5ecaa8);
      *(undefined4 *)((int)this + 0x4c) = 1;
      local_c = 0;
    }
  }
  return local_c;
}
