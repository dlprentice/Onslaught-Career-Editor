/* address: 0x0055f2a7 */
/* name: CDropship__FindSubstringW */
/* signature: short * __cdecl CDropship__FindSubstringW(short * haystack, short * needle) */


short * __cdecl CDropship__FindSubstringW(short *haystack,short *needle)

{
  short *psVar1;

  do {
    if (*haystack == 0) {
      return (short *)0x0;
    }
    psVar1 = needle;
    do {
      if ((*psVar1 == 0) || (*(short *)(((int)haystack - (int)needle) + (int)psVar1) != *psVar1))
      break;
      psVar1 = psVar1 + 1;
    } while (*(short *)(((int)haystack - (int)needle) + (int)psVar1) != 0);
    if (*psVar1 == 0) {
      return haystack;
    }
    haystack = haystack + 1;
  } while( true );
}
