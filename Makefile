all:
	@$(MAKE) userdata sshpublickeys

userdata:
	@$(MAKE) default $(USERDATA_FILES)

sshpublickeys:
	@$(MAKE) default $(SSH_PUBLIC_KEYS)

default:
	@true

#example.userdata: \
#	example.yaml example.sh set-fqdn.sh getconfig.py

#USERDATA=example
USERDATA=

%.userdata:
	./writemime.py -o $@ $^

USERDATA_FILES=$(addsuffix .userdata,$(USERDATA))

%.key.pub: %.key
	@echo ssh-keygen -y -f $< \> $@ &&			\
	 chmod go-rwx $< &&					\
	 ssh-keygen -y -f $< | sed "s/\$$/ root@$*/" > .$@ &&	\
	 test -s .$@ && mv .$@ || rm -f .$@

%.key:
	ssh-keygen -q -t ecdsa -b 256 -N '' -f $@

SSH_PUBLIC_KEYS=$(addsuffix .pub,$(wildcard *.key))

# normally ignored paths/patterns that should not be cleaned
CLEANIGNORE=.terraform .idea
CLEANOPTS=$(addprefix -e !,$(CLEANIGNORE))

clean:
	@if git clean -ndX $(CLEANOPTS) | grep .; then		\
	   printf 'Remove these files? (y/N) '; read ANS;	\
	   case $$ANS in [yY]*) git clean -fdX $(CLEANOPTS) ;;	\
			 *) exit 1 ;; esac			\
	 fi

.FORCE:
.PHONY: all userdata sshpublickeys default clean
