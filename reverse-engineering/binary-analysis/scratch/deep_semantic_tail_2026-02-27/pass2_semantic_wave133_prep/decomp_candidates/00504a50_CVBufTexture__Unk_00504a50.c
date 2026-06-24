/* address: 0x00504a50 */
/* name: CVBufTexture__Unk_00504a50 */
/* signature: void __fastcall CVBufTexture__Unk_00504a50(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CVBufTexture__Unk_00504a50(void *param_1)

{
  float fVar1;
  float *pfVar2;
  int iVar3;

  CCannon__Helper_0047c970(param_1);
  CVBufTexture__Unk_00504b40((int)param_1);
  if (*(int *)((int)param_1 + 0x214) != 0) {
    *(undefined4 *)((int)param_1 + 0x284) = *(undefined4 *)((int)param_1 + 0x280);
    if (*(int *)((int)param_1 + 0x168) != 2) {
      *(float *)((int)param_1 + 0x260) = *(float *)((int)param_1 + 0x260) + _DAT_005d8cb0;
    }
    fVar1 = *(float *)((int)param_1 + 0x260) * _DAT_005d8bd0;
    pfVar2 = (float *)((int)param_1 + 0x288);
    iVar3 = 6;
    *(float *)((int)param_1 + 0x260) = fVar1;
    *(float *)((int)param_1 + 0x280) = fVar1 + *(float *)((int)param_1 + 0x280);
    do {
      pfVar2[6] = *pfVar2;
      if (pfVar2[-8] == 0.0) {
        if (_DAT_005d856c < *pfVar2) {
          *pfVar2 = *pfVar2 - *pfVar2 * _DAT_005d858c;
        }
        if (*pfVar2 <= _DAT_005d856c) {
          *pfVar2 = 0.0;
        }
      }
      else {
        if (*pfVar2 < _DAT_005d8568) {
          *pfVar2 = (_DAT_005d8568 - *pfVar2) * _DAT_005d8bb0 + *pfVar2;
        }
        if (_DAT_005d8568 <= *pfVar2) {
          *pfVar2 = 1.0;
          pfVar2[-8] = 0.0;
        }
      }
      pfVar2 = pfVar2 + 1;
      iVar3 = iVar3 + -1;
    } while (iVar3 != 0);
  }
  return;
}
