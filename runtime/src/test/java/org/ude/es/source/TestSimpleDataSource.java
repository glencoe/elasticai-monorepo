package org.ude.es.source;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.ude.es.Checker;
import org.ude.es.comm.Posting;

class TestSimpleDataSource {

    private static class SimpleDataSourceChecker extends Checker {

        public DataSource<Integer> dataSource;

        public void givenDataSource() {
            dataSource = new DataSource<>("data");
            dataSource.bind(javaTwin);
        }

        public void whenDataIsSetTo(int value) {
            expected =
                new Posting(
                    javaTwin.getDomainAndIdentifier() + "/DATA/data",
                    "" + value
                );
            dataSource.set(value);
        }
    }

    private SimpleDataSourceChecker checker;

    @BeforeEach
    void init() {
        checker = new SimpleDataSourceChecker();
    }

    @Test
    void whenDataIsSetThenPostingIsSent() {
        checker.givenBroker();
        checker.givenJavaTwin("twin1234");
        checker.givenDataSource();
        checker.givenSubscriptionAtJavaTwinFor("/#");
        checker.whenDataIsSetTo(3);
        checker.thenPostingIsDelivered();
    }
}
