/* address: 0x00459b00 */
/* name: CFEPMultiplayerStart__SubObj8848__Process */
/* signature: void CFEPMultiplayerStart__SubObj8848__Process(void * this, int menu_state) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CFEPMultiplayerStart__SubObj8848__Process(void *this,int menu_state)

{
  float fVar1;
  int in_ECX;
  float *pfVar2;
  int iVar3;
  int iVar4;

  if (ABS(*(float *)(in_ECX + 0x3460) - *(float *)(in_ECX + 0x3464)) <= _DAT_005d8568) {
    if (*(float *)(in_ECX + 0x3464) <= *(float *)(in_ECX + 0x3460)) {
      fVar1 = *(float *)(in_ECX + 0x3464) + _DAT_005d8568;
    }
    else {
      fVar1 = *(float *)(in_ECX + 0x3464) - _DAT_005d8568;
    }
  }
  else {
    fVar1 = (*(float *)(in_ECX + 0x3464) - *(float *)(in_ECX + 0x3460)) * _DAT_005d858c +
            *(float *)(in_ECX + 0x3460);
  }
  *(float *)(in_ECX + 0x3460) = fVar1;
  iVar4 = 0;
  pfVar2 = (float *)(in_ECX + 0x57c);
  do {
    iVar3 = 0;
    do {
      if (((this == (void *)0x0) && (iVar4 == *(int *)(in_ECX + 0x3468))) &&
         (iVar3 == *(int *)(in_ECX + 0x346c))) {
        fVar1 = *pfVar2 + _DAT_005d85c0;
      }
      else {
        fVar1 = *pfVar2 - _DAT_005d85c0;
      }
      *pfVar2 = fVar1;
      if (*pfVar2 < _DAT_005d856c) {
        *pfVar2 = 0.0;
      }
      if (_DAT_005d8568 < *pfVar2) {
        *pfVar2 = 1.0;
      }
      iVar3 = iVar3 + 1;
      pfVar2 = pfVar2 + 1;
    } while (iVar3 < 6);
    iVar4 = iVar4 + 1;
  } while (iVar4 < 0x32);
  iVar4 = *(int *)(in_ECX + 0x347c) + 1;
  *(int *)(in_ECX + 0x347c) = iVar4;
  if ((this == (void *)0x0) && (0x2ee < iVar4)) {
    CFrontEnd__SetPage(&DAT_0089d758,0xc,0);
  }
  return;
}
