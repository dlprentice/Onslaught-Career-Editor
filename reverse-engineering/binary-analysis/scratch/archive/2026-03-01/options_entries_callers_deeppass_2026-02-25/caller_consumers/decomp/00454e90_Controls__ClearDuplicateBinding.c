/* address: 0x00454e90 */
/* name: Controls__ClearDuplicateBinding */
/* signature: void __cdecl Controls__ClearDuplicateBinding(int key_code, short scan_code, int device_code) */


/* Iterates the persisted controls/options entry table (DAT_008892d8).
   For each active entry, checks both 12-byte binding slots (+0x08 and +0x14).
   If slot matches (key_code, scan_code) and the device_code falls into the same device category as
   the existing binding's device, clears the binding (sets slot.key_code = -1).
   Used during control remapping to enforce unique bindings. */

void __cdecl Controls__ClearDuplicateBinding(int key_code,short scan_code,int device_code)

{
  int iVar1;
  int iVar2;
  int *piVar3;
  int iVar4;
  undefined4 *puVar5;

  if (DAT_008892dc != -1) {
    puVar5 = &DAT_008892dc;
    do {
      if (*(char *)(puVar5 + -1) != '\0') {
        piVar3 = puVar5 + 1;
        iVar4 = 2;
        do {
          if ((*piVar3 == key_code) && ((short)piVar3[2] == scan_code)) {
            switch(device_code) {
            default:
              iVar2 = 1;
              break;
            case 4:
            case 6:
              iVar2 = 3;
              break;
            case 5:
            case 7:
              iVar2 = 2;
              break;
            case 8:
            case 9:
            case 10:
              iVar2 = 4;
              break;
            case 0xb:
            case 0xd:
              iVar2 = 5;
              break;
            case 0xc:
            case 0xe:
              iVar2 = 6;
              break;
            case 0xf:
            case 0x10:
            case 0x11:
              iVar2 = 7;
            }
            switch(piVar3[1]) {
            default:
              iVar1 = 1;
              break;
            case 4:
            case 6:
              iVar1 = 3;
              break;
            case 5:
            case 7:
              iVar1 = 2;
              break;
            case 8:
            case 9:
            case 10:
              iVar1 = 4;
              break;
            case 0xb:
            case 0xd:
              iVar1 = 5;
              break;
            case 0xc:
            case 0xe:
              iVar1 = 6;
              break;
            case 0xf:
            case 0x10:
            case 0x11:
              iVar1 = 7;
            }
            if (iVar2 == iVar1) {
              *piVar3 = -1;
            }
          }
          piVar3 = piVar3 + 3;
          iVar4 = iVar4 + -1;
        } while (iVar4 != 0);
      }
      piVar3 = puVar5 + 8;
      puVar5 = puVar5 + 8;
    } while (*piVar3 != -1);
  }
  return;
}
