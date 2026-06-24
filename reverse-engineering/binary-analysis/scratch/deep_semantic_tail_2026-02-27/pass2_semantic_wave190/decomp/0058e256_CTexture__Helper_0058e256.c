/* address: 0x0058e256 */
/* name: CTexture__Helper_0058e256 */
/* signature: uint __thiscall CTexture__Helper_0058e256(void * this, void * param_1, int param_2) */


uint __thiscall CTexture__Helper_0058e256(void *this,void *param_1,int param_2)

{
  char *pcVar1;
  uint uVar2;
  char cVar3;
  char *pcVar4;
  void *pvStack_14;
  void *local_8;

  pcVar1 = *(char **)((int)param_1 + 8);
  uVar2 = 0;
  if ((pcVar1 == (char *)0x0) || (cVar3 = *pcVar1, pcVar4 = pcVar1, local_8 = this, cVar3 == '\0'))
  {
    uVar2 = 0xf0000;
  }
  else {
    do {
      if (cVar3 < 'x') {
        if ((cVar3 == 'w') || (cVar3 == 'a')) {
          pvStack_14 = (void *)0x3;
          uVar2 = uVar2 | 0x80000;
        }
        else {
          if (cVar3 != 'b') {
            if (cVar3 == 'g') goto LAB_0058e2d1;
            if (cVar3 != 'r') goto LAB_0058e2db;
            goto LAB_0058e296;
          }
LAB_0058e2c7:
          pvStack_14 = (void *)0x2;
          uVar2 = uVar2 | 0x40000;
        }
      }
      else if (cVar3 == 'x') {
LAB_0058e296:
        pvStack_14 = (void *)0x0;
        uVar2 = uVar2 | 0x10000;
      }
      else {
        if (cVar3 != 'y') {
          if (cVar3 != 'z') goto LAB_0058e2db;
          goto LAB_0058e2c7;
        }
LAB_0058e2d1:
        pvStack_14 = (void *)0x1;
        uVar2 = uVar2 | 0x20000;
      }
      if ((pcVar4 != pcVar1) && (pvStack_14 <= local_8)) {
LAB_0058e2db:
        CTexture__Helper_0058c893(*(void **)this,(int)param_1,0x7d3,0x5eca94);
        *(undefined4 *)((int)this + 0x4c) = 1;
        return 0;
      }
      cVar3 = pcVar4[1];
      pcVar4 = pcVar4 + 1;
      local_8 = pvStack_14;
    } while (cVar3 != '\0');
  }
  return uVar2;
}
